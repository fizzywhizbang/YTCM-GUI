'''
Created on Aug 2, 2015
https://github.com/izderadicka?tab=repositories
@author: ivan
'''
import urwid
from collections import deque
from threading import Thread
import threading

class UnknownCommand(Exception):
    def __init__(self,cmd):
        Exception.__init__(self,'Uknown command: %s'%cmd)

class Command(object):
    """ Base class to manage commands in commander
similar to cmd.Cmd in standard library
just extend with do_something  method to handle your commands"""

    def __init__(self,quit_commands=['q','quit','exit'], help_commands=['help','?', 'h']):
        self._quit_cmd=quit_commands
        self._help_cmd=help_commands
        
    def __call__(self,line):
        tokens=line.split()
        cmd=tokens[0].lower()
        #because of potential spaces in names as on arg I will split at the comma
        line=line.replace(cmd + " ","").replace(", ","")
        tokens2=line.split(",")
        args=tokens2[0:]
        if cmd in self._quit_cmd:
            return Commander.Exit
        elif cmd in self._help_cmd:
            return self.help(args[0] if args else None)
        elif hasattr(self, 'do_'+cmd):
            return getattr(self, 'do_'+cmd)(*args)
        else:
            raise UnknownCommand(cmd)
        
    def help(self,cmd=None):
        def std_help():
            qc='|'.join(self._quit_cmd)
            hc ='|'.join(self._help_cmd)
            res='Type [%s] command_name to get more help about particular command\n' % hc
            res+='Type [%s] to quit program\n' % qc
            cl=[name[3:] for name in dir(self) if name.startswith('do_') and len(name)>3]
            res += 'Available commands: %s' %(' '.join(sorted(cl)))
            return res
        if not cmd:
            return std_help()
        else:
            try:
                fn=getattr(self,'do_'+cmd)
                doc=fn.__doc__
                return doc or 'No documentation available for %s'%cmd
            except AttributeError:
                return std_help()
 
class FocusMixin(object):
    def mouse_event(self, size, event, button, x, y, focus):
        if focus and hasattr(self, '_got_focus') and self._got_focus:
            self._got_focus()
        return super(FocusMixin,self).mouse_event(size, event, button, x, y, focus)    
    
class ListView(FocusMixin, urwid.ListBox):
    def __init__(self, model, got_focus, max_size=None):
        urwid.ListBox.__init__(self,model)
        self._got_focus=got_focus
        self.max_size=max_size
        self._lock=threading.Lock()
        
    def add(self,line):
        with self._lock:
            was_on_end=self.get_focus()[1] == len(self.body)-1
            if self.max_size and len(self.body)>self.max_size:
                del self.body[0]
            self.body.append(urwid.Text(line))
            last=len(self.body)-1
            if was_on_end:
                self.set_focus(last,'above')
        
    

class Input(FocusMixin, urwid.Edit):
    signals=['line_entered']
    def __init__(self, got_focus=None):
        urwid.Edit.__init__(self)
        self.history=deque(maxlen=1000)
        self._history_index=-1
        self._got_focus=got_focus
    
    def keypress(self, size, key):
        if key=='enter':
            line=self.edit_text.strip()
            if line:
                urwid.emit_signal(self,'line_entered', line)
                self.history.append(line)
            self._history_index=len(self.history)
            self.edit_text=u''
        if key=='up':
            
            self._history_index-=1
            if self._history_index< 0:
                self._history_index= 0
            else:
                self.edit_text=self.history[self._history_index]
        if key=='down':
            self._history_index+=1
            if self._history_index>=len(self.history):
                self._history_index=len(self.history) 
                self.edit_text=u''
            else:
                self.edit_text=self.history[self._history_index]
        else:
            urwid.Edit.keypress(self, size, key)
        


class Commander(urwid.Frame):
    """ Simple terminal UI with command input on bottom line and display frame above
similar to chat client etc.
Initialize with your Command instance to execute commands
and the start main loop Commander.loop().
You can also asynchronously output messages with Commander.output('message') """

    class Exit(object):
        pass
    
    PALLETE=[('reversed', urwid.WHITE, urwid.BLACK),
            ('header', 'white,bold', 'black', 'standout,underline','black,underline', '#88a'),
              ('normal', urwid.BLACK, urwid.WHITE),
              ('error', urwid.LIGHT_RED, urwid.BLACK),
              ('green', urwid.DARK_GREEN, urwid.WHITE),
              ('blue', urwid.LIGHT_BLUE, urwid.WHITE),
              ('magenta', urwid.DARK_MAGENTA, urwid.WHITE), ]
    
    
    def __init__(self, title, command_caption='Command:  (Tab to switch focus to upper frame, where you can scroll text)', cmd_cb=None, max_size=1000):
        self.header=urwid.Text(title)
        self.model=urwid.SimpleListWalker([])
        self.body=ListView(self.model, lambda: self._update_focus(False), max_size=max_size )
        self.input=Input(lambda: self._update_focus(True))
        foot=urwid.Pile([urwid.AttrMap(urwid.Text(command_caption), 'reversed'),
                        urwid.AttrMap(self.input,'normal')])
        urwid.Frame.__init__(self, 
                             urwid.AttrWrap(self.body, 'normal'),
                             urwid.AttrWrap(self.header, 'header'),
                             foot)
        self.set_focus_path(['footer',1])
        self._focus=True
        urwid.connect_signal(self.input,'line_entered',self.on_line_entered)
        self._cmd=cmd_cb
        self._output_styles=[s[0] for s in self.PALLETE]
        self.eloop=None
        
    def loop(self, handle_mouse=False):
        self.eloop=urwid.MainLoop(self, self.PALLETE, handle_mouse=handle_mouse)
        self._eloop_thread=threading.current_thread()
        self.eloop.run()
        
    def on_line_entered(self,line):
        if self._cmd:
            try:
                res = self._cmd(line)
            except Exception as e:
                self.output('Error: %s'%e, 'error')
                return
            if res==Commander.Exit:
                raise urwid.ExitMainLoop()
            elif res:
                self.output(str(res))
        else:
            if line in ('q','quit','exit'):
                raise urwid.ExitMainLoop()
            else:
                self.output(line)
    
    def output(self, line, style=None):
        if style and style in self._output_styles:
                line=(style,line) 
        self.body.add(line)
        #since output could be called asynchronously form other threads we need to refresh screen in these cases
        if self.eloop and self._eloop_thread != threading.current_thread():
            self.eloop.draw_screen()
        
        
    def _update_focus(self, focus):
        self._focus=focus
        
    def switch_focus(self):
        if self._focus:
            self.set_focus('body')
            self._focus=False
        else:
            self.set_focus_path(['footer',1])
            self._focus=True
        
    def keypress(self, size, key):
        if key=='tab':
            self.switch_focus()
        return urwid.Frame.keypress(self, size, key)
        
    
if __name__=='__main__':
    class TestCmd(Command):
        def do_echo(self, *args):
            '''echo - Just echos all arguments'''
            return ' '.join(args)
        def do_raise(self, *args):
            raise Exception('Some Error')
        
    c=Commander('Test', cmd_cb=TestCmd())
    
    #Test asynch output -  e.g. comming from different thread
    import time
    def run():
        while True:
            time.sleep(1)
            c.output('Tick', 'green')
    t=Thread(target=run)
    t.daemon=True
    t.start()
    
    #start main loop
    c.loop()
        

