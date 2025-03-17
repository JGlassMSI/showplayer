import pathlib
import pickle
import tkinter as tk
from typing import reveal_type

from showplayer_cuelist import showplayer
from Cuelist import Cuelist

def test_import_show(tmp_path: pathlib.Path):
    root = tk.Tk()
    root.wm_title("727 Show Player")
    root.protocol('WM_DELETE_WINDOW', root.destroy)
    player = showplayer(master=root, title="727 Show Player")

    tmp_cuelist = Cuelist("tmp", cues=[])
    tmp_showfile = tmp_path / "show.727show"
    tmp_showfile.touch()
    with open(tmp_showfile, 'wb') as f:
        reveal_type(f)
        pickle.dump(tmp_cuelist, f)
    # Show has been saved here

    show = player.importShow(tmp_showfile)
    #Show has been imported here

    assert len(player.showList) == 2 # includes default empty show
    assert not any(show.cues for show in player.showList)
