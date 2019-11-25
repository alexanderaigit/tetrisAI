Tetris AI bot is divided into three python files i.e. player.py, tetris_ai.py, tetris_model.py. Contained files worked as suggested. 

How to execute TetrisAIbot:
1)just run "player.py" file.

important parameters:
1)change speed of peices: player.py and line 22 (lager the value slower the speed)
2)change background color of game: player.py, line 24 (change the #VALUE)
3)change height and width of gameBoard: tetris_model.py, line 68, line 69	

If user want to play the game (without AI) follow the 3 steps procedure:
1) open player.py
2) comment "from tetris_ai import TETRIS_AI" (AI import)
3) uncomment "TETRIS_AI = None"
