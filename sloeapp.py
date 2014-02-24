
import logging
import optparse
import os
from pprint import pprint
import sys
import sloelib
import sloeyoutube

from sloegeneratecfg import SloeGenerateCfg

class SloeApp:

    def get_global(self, name):
        glb_cfg = sloelib.SloeConfig.inst()
        return glb_cfg.get_value("global", name)


    def enter(self):
        parser = optparse.OptionParser("usage: %prog [options] command")
        parser.add_option("--dryrun",
                          action="store_true", dest="dryrun", default=False,
                          help="perform functions but do not write files")
        parser.add_option("--dump",
                          action="store_true", dest="dump", default=False,
                          help="dump output after processing")
        parser.add_option("--final",
                          action="store_true", dest="final", default=False,
                          help="generate_cfg for final directory")
        parser.add_option("--keepsandbox",
                          action="store_true", dest="keepsandbox", default=False,
                          help="do not delete sandbox files after completion")
        parser.add_option("--prerenderabort",
                          action="store_true", dest="prerenderabort", default=False,
                          help="abort before the first render command, leaving sandbox files in place")
        parser.add_option("--postrenderabort",
                          action="store_true", dest="postrenderabort", default=False,
                          help="abort after the first render command, leaving sandbox files in place")      
        parser.add_option("--reset-sloeid",
                          action="store_true", dest="resetsloeid", default=False,
                          help="reset sloeid values in Youtube tags")
        parser.add_option("--script-dir",
                          action="store_true", dest="script_dir", default=os.path.dirname(os.path.abspath(__file__)),
                          help="Path to the directory containing %s" % os.path.dirname(__file__))        
        parser.add_option("-v", "--verbose",
                          action="store_true", dest="verbose", default=False,
                          help="verbose output")
        (self.options, self.args) = parser.parse_args()
        self.params = self.args[1:]
        logging.basicConfig(format="#%(levelname)s:%(filename)s::%(funcName)s#%(lineno)d at %(asctime)s\n%(message)s")
        glb_cfg = sloelib.SloeConfig.inst()
        logging.info("Loading global config file config.cfg")
        glb_cfg.appendfile('config.cfg')
        loglevelstr = glb_cfg.get_value("global", "loglevel")
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

        # Load plugins once config is ready
        sloelib.SloePlugInManager.inst().load_plugins()

        if len(self.args) == 0:
            parser.error("Please supply a command argument")
        else:
            command = self.args[0]
            plugin_commands = sloelib.SloePlugInManager.inst().commands
            if command in plugin_commands.keys():
                    
                command_spec = plugin_commands[command]
                sloelib.SloePlugInManager.inst().call_plugin(
                    command_spec["plugin"],
                    command_spec["method"],
                    params=self.args[1:],
                    options=self.options)                
            else:        
                valid_commands = ["auth", "dumptree", "lsoutput", "lswork", "sync", "verifytree"] + plugin_commands.keys()
                if command not in valid_commands:
                    parser.error("Command not valid - must be one of %s" % ", ".join(valid_commands))
    
                logging.info("Command: %s" % " ".join(self.args))
                getattr(self, command)(*self.args[1:])


    def auth(self):
        session_r = sloeyoutube.SloeYouTubeSession("r")
        session_r.get_session()
        session_w = sloeyoutube.SloeYouTubeSession("w")
        session_w.get_session()


    def dowork(self, *subtrees):
        glb_cfg = sloelib.SloeConfig.inst()
        for subtree in subtrees:
            tree = sloelib.SloeTrees.inst().get_tree()
            executor = sloelib.SloeLocalExec(tree)
            work_manager = sloelib.SloeWorkManager()
            work = work_manager.get_all_work(tree)
            sloelib.SloeExecUtil.do_work(executor, work)



    def dumptree(self):
        session_r = sloeyoutube.SloeYouTubeSession("r")
        tree = sloeyoutube.SloeYouTubeTree(session_r)
        tree.read()
        print tree


    def generatecfg(self, *params):
        sloelib.SloeTrees.inst().get_tree()
        sloelib.SloePlugInManager.inst().call_plugin(
            "generatecfg",
            "command_generatecfg",
            params=params)


    def lsoutput(self, *subtrees):
        glb_cfg = sloelib.SloeConfig.inst()
        for subtree in subtrees:
            tree = sloelib.SloeTrees.inst().get_tree()
            outpututil = sloelib.SloeOutputUtil(tree)
            outputdefs = outpututil.derive_outputdefs()
            pprint(outputdefs)


    def lswork(self, *subtrees):
        glb_cfg = sloelib.SloeConfig.inst()
        for subtree in subtrees:
            tree = sloelib.SloeTrees.inst().get_tree()
            work_manager = sloelib.SloeWorkManager(tree)
            work = work_manager.get_all_work(tree)
            pprint(work)


    def sync(self):
        session_w = sloeyoutube.SloeYouTubeSession("w")
        tree = sloeyoutube.SloeYouTubeTree(session_w)
        tree.read()
        tree.write()


    def verifytree(self, *subtrees):
        glb_cfg = sloelib.SloeConfig.inst()
        for subtree in subtrees:
            logging.debug("Beginning tree verification for %s" % tree_name)
            tree = sloelib.SloeTrees.inst().get_tree()
            if (sloelib.SloeConfig.get_option("dump")):
                pprint(tree)

if __name__ == "__main__":
    SloeApp().enter()
    print "Done."