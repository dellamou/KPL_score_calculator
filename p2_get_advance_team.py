from collections import defaultdict
import itertools
import copy
import dill as pickle

# 一些常量
bo5_score = [[0, 3], [1, 3], [2, 3], [3, 2], [3, 1], [3, 0]]
WIN       = 0 # 胜场
LOSE      = 1 # 负场
NET_WIN   = 2 # 净胜分
SCORE     = 3 # 积分

# 从文件中读取数据
# 读取积分榜
with open("est_board.pkl", "rb") as f:
    _est_board = pickle.load(f)

# 读取胜负关系
with open("win_lose.pkl", "rb") as f:
    _win_lose = pickle.load(f)

# 读取接下来的比赛
with open("next_game_play.pkl", "rb") as f:
    _game_play = pickle.load(f)

# 获取能够晋级的所有队伍
def get_advance_team(est_board, win_lose, game_play, advance_num):
    advance_teams = defaultdict(list)
    for tmp_board in est_board:
        game_result = tmp_board[0]
        board = tmp_board[1]

        # 考虑胜负关系的时候还要把estimated board的win_lose也考虑进去
        tmp_win_lose = copy.deepcopy(win_lose)
        for i in range(len(game_play)):
            team1 = game_play[i][0]
            team2 = game_play[i][1]
            
            team1_result = game_result[i][0]
            team2_result = game_result[i][1]

            if team1_result > team2_result:
                tmp_win_lose[team1].append(team2)
            else:
                tmp_win_lose[team2].append(team1)

        # get the top n teams
        top_n_teams = list(board.keys())[:advance_num]

        # 如果积分相同，按照净胜分排序，如果净胜分相同，按照胜负关系排序，如果胜负关系相同，则都晋级
        for i in range(advance_num, len(board)):
                next_team = list(board.keys())[i]
                if board[next_team][NET_WIN] == board[top_n_teams[-1]][NET_WIN] and board[next_team][SCORE] == board[top_n_teams[-1]][SCORE]:
                    # 检查胜负关系时需要把所有小分相同队伍的胜负关系都考虑进去
                    all_same_net_win_teams = [team for team in board.keys() if board[team][NET_WIN] == board[top_n_teams[-1]][NET_WIN] and board[team][SCORE] == board[top_n_teams[-1]][SCORE]]
                    # 先把小分相同队伍从top_n_teams中去掉
                    for team in all_same_net_win_teams:
                        if team in top_n_teams:
                            top_n_teams.remove(team)
                    # 两两检查胜负关系
                    pair_teams = list(itertools.combinations(all_same_net_win_teams, 2))
                    for pair_team in pair_teams:
                        team1 = pair_team[0]
                        team2 = pair_team[1]
                        if team1 in tmp_win_lose.keys() and team2 in tmp_win_lose[team1]:
                            top_n_teams.append(team1)
                        elif team2 in tmp_win_lose.keys() and team1 in tmp_win_lose[team2]:
                            top_n_teams.append(team2)
                        else:
                            top_n_teams.append(team1)
                            top_n_teams.append(team2)
        tuple_top_n_teams = tuple(top_n_teams)
        advance_teams[tuple_top_n_teams].append(tmp_board)
    return advance_teams

# 根据晋级队伍获取加赛情况（晋级队伍中有超过advance_num个队伍则末尾小分相同的队伍需要加赛）
def get_extra_game(advance_teams, advance_num):
    extra_game_teams = defaultdict(list)
    for advance_teams_key in advance_teams.keys():
        if len(advance_teams_key) > advance_num:
            # 末尾小分相同的队伍需要加赛
            for board in advance_teams[advance_teams_key]:
                #  get the 4th team's score
                tie_game_score = board[1][list(board[1])[advance_num-1]][SCORE]
                # get all the teams with the same score
                same_score_teams = [team for team in board[1].keys() if board[1][team][SCORE] == tie_game_score]
                same_score_teams = tuple(same_score_teams)
                extra_game_teams[same_score_teams].append(board)
    return extra_game_teams

# 获取晋级队伍
advance_teams = get_advance_team(_est_board, _win_lose, _game_play, 4)

# 获取加赛情况
extra_game_teams = get_extra_game(advance_teams, 4)

# 保存结果为pkl文件
# 保存晋级队伍
with open("advance_teams.pkl", "wb") as f:
    pickle.dump(advance_teams, f)
# 保存加赛情况
with open("extra_game_teams.pkl", "wb") as f:
    pickle.dump(extra_game_teams, f)

# 保存结果为txt文件
# 保存晋级队伍
with open("advance_teams.txt", "w") as f:
    for key, value in advance_teams.items():
        f.write("晋级队伍: {}\n".format(key))
        for tmp_board in value:
            f.write("Match result: {}\n".format(tmp_board[0]))
            f.write("Board:\n")
            for team, info in tmp_board[1].items():
                f.write("{:<10} {:<10} {:<10} {:<10} {:<10}\n".format(team, info[0], info[1], info[2], info[3]))
            f.write("\n")
# 保存加赛情况
with open("extra_game_teams.txt", "w") as f:
    for key, value in extra_game_teams.items():
        f.write("加赛队伍: {}\n".format(key))
        for tmp_board in value:
            f.write("比赛结果:\n")
            for i in range(len(_game_play)):
                team1, team2 = _game_play[i]
                score1, score2 = tmp_board[0][i]
                f.write("{:<5} vs. {:<5}\t{}:{}\n".format(team1, team2, score1, score2))
            f.write("积分榜:\n")
            for team, info in tmp_board[1].items():
                f.write("{:<10} {:<10} {:<10} {:<10} {:<10}\n".format(team, info[0], info[1], info[2], info[3]))
            f.write("\n")
