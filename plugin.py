import time, signal, sys
import RPi.GPIO as GPIO


class Plugin:
  FILTER = []
  PATHACV = "gps.anchorChainValue"
  CONFIG=[
    {
      'name': 'circumference',
      'description': 'Define the circumference of anchor winch im [mm] (default: 30)',
      'default': '30'
    },
    {
      'name': 'gpio_reed',
      'description': 'Define gpio where reed relais is sensed (default is 17 => GPI17 on pin 11)',
      'default': '17'
    },
    {
      'name': 'gpio_up',
      'description': 'Define gpio where the up is sensed (default is 27 => GPI27 on pin 13)',
      'default': '27'
    },
    {
      'name': 'gpio_down',
      'description': 'Define gpio where the up is sensed (default is 22 => GPI22 on pin 15)',
      'default': '22'
    },
    {
      'name': 'pulldown',
      'description': 'Define if using internal RPi pull up/down 0 => No, 1= Pull down, 2=Pull up (default is 2)',
      'default': '2'
    }    
  ]
  @classmethod
  def pluginInfo(cls):
    """
    the description for the module
    @return: a dict with the content described below
            parts:
               * description (mandatory)
               * data: list of keys to be stored (optional)
                 * path - the key - see AVNApi.addData, all pathes starting with "gps." will be sent to the GUI
                 * description
    """
    return {
      'description': 'seatalk 1 protocol reader',
      'config': cls.CONFIG,
      'data': [
        {
          'path': cls.PATHACV,
          'description': 'anchor chain value',
        },
      ]
    }

  def __init__(self,api):
    """
        initialize a plugins
        do any checks here and throw an exception on error
        do not yet start any threads!
        @param api: the api to communicate with avnav
        @type  api: AVNApi
    """
    self.api = api # type: AVNApi
    #we register an handler for API requests
    self.circumference=0.30
    self.anchorChainValue = 0.0
    self.gpio_reed='17'
    self.gpio_up='27'
    self.gpio_up='22'
    self.pulldown='2'
    self.isConnected=False
    if hasattr(self.api,'registerEditableParameters'):
      self.api.registerEditableParameters(self.CONFIG,self._changeConfig)
    if hasattr(self.api,'registerRestart'):
      self.api.registerRestart(self._apiRestart)
    self.changeSequence=0
    self.startSequence=0

  def _apiRestart(self):
    self.startSequence+=1
    self.changeSequence+=1

  def _changeConfig(self,newValues):
    self.api.saveConfigValues(newValues)
    self.changeSequence+=1

  def getConfigValue(self,name):
    defaults=self.pluginInfo()['config']
    for cf in defaults:
      if cf['name'] == name:
        return self.api.getConfigValue(name,cf.get('default'))
    return self.api.getConfigValue(name)

  def run(self):
    startSequence=self.startSequence
    while startSequence == self.startSequence:
      self.runInternal()

  def reed_callback(channel):
    self.anchorChainValue += 0.0

  def up_callback(channel):
    self.anchorChainValue += 0.0

  def down_callback(channel):
    self.anchorChainValue -= 0.0

  def runInternal(self):
    """
    the run method
    this will be called after successfully instantiating an instance
    this method will be called in a separate Thread
    The plugin sends every 10 seconds the depth value via seatalk
    @return:
    """
    changeSequence=self.changeSequence
    seq=0
    self.api.log("started")
    self.api.setStatus('STARTED', 'running')
    enabled=self.getConfigValue('enabled')
    if enabled is not None and enabled.lower()!='true':
      self.api.setStatus("INACTIVE", "disabled by config")
      return

    while changeSequence == self.changeSequence:
      #if not self.isConnected:
        #return {'status': 'not connected'}

      try:
        self.circumference=self.getConfigValue('circumference')
        self.gpio_reed=self.getConfigValue('gpio_reed')
        self.gpio_up=self.getConfigValue('gpio_up')
        self.gpio_down=self.getConfigValue('gpio_down')
        self.pulldown=self.getConfigValue('pulldown')

      except Exception as e:
        self.api.setStatus("ERROR", "config error %s "%str(e))

      errorReported=False

      try:
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(int(self.gpio_reed), GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(int(self.gpio_up),   GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(int(self.gpio_down), GPIO.IN, pull_up_down=GPIO.PUD_UP)

      except Exception as e:
        if not errorReported:
          self.api.setStatus("ERROR","unable to setup GPIO%s: %s"%(self.gpio_reed, str(e)))
          self.api.error("unable to setup GPIO%s: %s" % (self.gpio_reed, str(e)))
          errorReported=True
        else:
          self.api.error("unable to setup GPIO%s: %s" % (self.gpio_reed, str(e)))

      '''
      try:
        GPIO.add_event_detect(int(self.gpio_reed), GPIO.FALLING, callback=reed_callback, bouncetime=100)  
        GPIO.add_event_detect(int(self.gpio_up), GPIO.FALLING, callback=up_callback, bouncetime=300)  
        GPIO.add_event_detect(int(self.gpio_down), GPIO.FALLING, callback=down_callback, bouncetime=300)  
      except Exception as e:
        self.api.error("unable to connect GPIO%s: %s" % (self.gpio_reed, str(e)))
        pass
      '''

      self.api.setStatus("NMEA","connected to GPIO%s" % (self.gpio_reed))
      self.api.log("connected to GPIO%s" % (self.gpio_reed))
      self.isConnected=True

      lastAnchorChainValue = -1.0
      lastReed = GPIO.input(int(self.gpio_reed))

      while(True):
          source='internal'
          try:
            curIncrement = 0.0

            if (GPIO.input(int(self.gpio_up)) == True):
              curIncrement = float(self.circumference) * float(0.001)
            elif (GPIO.input(int(self.gpio_down)) == True):
              curIncrement = float(self.circumference) * float(-0.001)

            newReed = GPIO.input(int(self.gpio_reed))

            if ((newReed == False) and (newReed != lastReed)):
              self.anchorChainValue = float(self.anchorChainValue) + float(curIncrement)
              self.api.addData(self.PATHACV, float(self.anchorChainValue),source=source)

            lastReed = newReed

          except Exception as e:
            self.api.error("GPIO%s: %s" % (self.gpio_reed, str(e)))
            pass

          time.sleep(0.01)
