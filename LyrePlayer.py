import asyncio
import mido
import pynput.keyboard
import time

mid = mido.MidiFile('./MIDIs/Canon in C - Johann Pachelbel.mid', clip=True)

keyDict = {
	48: "z",
	50: "x",
	52: "c",
	53: "v",
	55: "b",
	57: "n",
	59: "m",
	60: "a",
	62: "s",
	64: "d",
	65: "f",
	67: "g",
	69: "h",
	71: "j",
	72: "q",
	74: "w",
	76: "e",
	77: "r",
	79: "t",
	81: "y",
	83: "u"
}

START_KEY = [pynput.keyboard.KeyCode.from_char("`")]
STOP_KEY = [pynput.keyboard.Key.space]

class LyrePlayer:
    def __init__(self):
        self.songKeyDict = None
        self.playingEventLoop = asyncio.get_event_loop()
        self.curPressedKey = set()
        self.playTaskActive = False 

    def start(self):
        pynput.keyboard.Listener(on_press=self.on_press, on_release=self.on_release).start()
        self.playingEventLoop.run_forever()


    def on_press(self, key):
        self.curPressedKey.add(key)

        if not self.playTaskActive and all(key in self.curPressedKey for key in START_KEY):
            for key in self.curPressedKey:
                self.playingEventLoop.call_soon_threadsafe(lambda: self.playingEventLoop.create_task(self.play()))
                self.playTaskActive = True
            
        elif all(key in self.curPressedKey for key in STOP_KEY):
            self.playTaskActive = False


    def on_release(self, key):
        self.curPressedKey.discard(key)


    async def play(self):
        keyboard = pynput.keyboard.Controller()

        print("start Playing")
        playTime = time.time()
        for msg in mid:
            
            #check for stop
            if not self.playTaskActive:
                print("stop playing")
                for key in self.curPressedKey.copy():
                    keyboard.release(key)
                return
                
            if msg.time > 0:
                await asyncio.sleep(msg.time - (time.time() - playTime))
                playTime += msg.time

            #press key
            if msg.type == 'note_on' or msg.type == 'note_off':
                if msg.type == "note_on" and msg.velocity != 0:
                    if key := keyDict.get(msg.note):
                        keyboard.press(key)
                        await asyncio.sleep(0.01)
                        keyboard.release(key)

        self.playTaskActive = False
        print("Finsih Playing")

if __name__ == "__main__":
    # print("sleep for 2 second")
    LyrePlayer().start()