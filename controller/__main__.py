import argparse

parser = argparse.ArgumentParser()
parser.add_argument('program', choices=['showplayer', 'showmaker'])
args = parser.parse_args()

if args.program == 'showplayer': 
    from .showplayer_cuelist import main as player_main
    player_main()
elif args.program == 'showmaker':
    from .showmaker_Cuelist import main as maker_main
    maker_main()