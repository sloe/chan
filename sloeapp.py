
import logging
import optparse
import os
import sys
import sloelib
import sloeyoutube

class SloeApp:

  def get_global(self, name):
    glb_cfg = sloelib.SloeConfig.get_global()
    return glb_cfg.get("global", name)


  def enter(self):
    parser = optparse.OptionParser("usage: %prog [options] command")
    parser.add_option("-z", "--dryrun",
                  action="store_true", dest="dryrun", default=False,
                  help="perform functions but do not write files")
    parser.add_option("--final",
                  action="store_true", dest="final", default=False,
                  help="generate_cfg for final directory")
    (self.options, self.args) = parser.parse_args()
    self.params = self.args[1:]
    logging.basicConfig(format="#%(levelname)s:%(filename)s::%(funcName)s#%(lineno)d at %(asctime)s\n%(message)s")
    glb_cfg = sloelib.SloeConfig.get_global()
    logging.info("Loading global config file config.cfg")
    glb_cfg.appendfile('config.cfg')
    loglevelstr = glb_cfg.get("global", "loglevel")
    if loglevelstr == 'DEBUG':
      self.loglevel = logging.DEBUG
    elif loglevelstr == 'INFO':
      self.loglevel = logging.INFO
    elif loglevelstr == 'WARNING':
      self.loglevel = logging.WARNING
    elif loglevelstr == 'ERROR':
      self.loglevel = logging.ERROR
    else:
      raise sloelib.SloeError("Invalid loglevel in config")
    logging.getLogger().setLevel(self.loglevel)

    glb_cfg.set_options(self.options)

    if len(self.args) == 0:
      parser.error("Please supply a command argument")
    else:
      valid_commands = ("auth", )
      command = self.args[0]
      if command not in valid_commands:
        parser.error("Command not valid - must be one of %s" % ", ".join(valid_commands))

      logging.info("Command: %s" % " ".join(self.args))
      getattr(self, command)()


  def auth(self):
    session_r = sloeyoutube.SloeYouTubeSession("r")
    session_r.get_session()
    session_w = sloeyoutube.SloeYouTubeSession("w")
    session_w.get_session()

if __name__ == "__main__":
  SloeApp().enter()
