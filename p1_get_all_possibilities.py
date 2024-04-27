from collections import defaultdict
import itertools
import copy
import dill as pickle

# 一些常量
bo5_score = [[0, 3], [1, 3], [2, 3], [3, 2], [3, 1], [3, 0]]
WIN     = 0 # 胜场
LOSE    = 1 # 负场
NET_WIN = 2 # 净胜分
SCORE   = 3 # 积分

# 记录每个战队积分情况
# 胜场、负场、净胜分、积分
board = defaultdict(lambda: [0, 0, 0, 0])

# 记录战队间的胜负关系
win_lose = defaultdict(list)

def update_board(board, team1, team2, score1, score2):
    # 净胜分
    net_win = abs(score1 - score2)

    # 根据胜负情况更新积分和胜负场次
    if score1 > score2:
        board[team1][WIN] += 1
        board[team2][LOSE] += 1
        board[team1][NET_WIN] += net_win
        board[team2][NET_WIN] -= net_win
        board[team1][SCORE] += 1
    else:
        board[team1][LOSE] += 1
        board[team2][WIN] += 1
        board[team1][NET_WIN] -= net_win
        board[team2][NET_WIN] += net_win
        board[team2][SCORE] += 1

# 获取用户输入
print("请输入所有战队的名字, 以空格分隔, 无需区分大小写")
teams = input().strip().split()
teams = [team.lower() for team in teams]

print("参加比赛的战队有: ", teams)

# 所有比赛的可能性
all_games = list(itertools.combinations(teams, 2))
print("本轮所有比赛: ", all_games)

# 获取已有的比赛结果
print("请输入本轮已有的比赛结果, 格式为: A B 3 2, 表示A战队以3比2战胜B战队")
print("输入end或空回车结束输入")
while True:
    line = input().strip()
    if line == "end" or line == "":
        break
    team1, team2, score1, score2 = line.split()
    score1, score2 = int(score1), int(score2)
    team1, team2 = team1.lower(), team2.lower()
    # check if the team is in the list
    if team1 not in teams or team2 not in teams:
        print("输入的战队不在列表中, 请重新输入")
        continue
    # check if the team is in the all_games
    if (team1, team2) in all_games:
        all_games.remove((team1, team2))
    elif (team2, team1) in all_games:
        all_games.remove((team2, team1))
    else:
        print("输入的比赛已经存在, 请重新输入")
        continue
    
    update_board(board, team1, team2, score1, score2)
    if score1 > score2:
        win_lose[team1].append(team2)
    else:
        win_lose[team2].append(team1)

# 将当前积分榜按照积分、净胜分、胜场排序排序
board = dict(sorted(board.items(), key=lambda x: (x[1][SCORE], x[1][NET_WIN], x[1][WIN]), reverse=True))
print("当前积分榜: ", board)

print("本轮赛程还需要比赛的队伍:", all_games)

# 计算所有可能的比分
all_possible_scores = list(itertools.product(bo5_score, repeat=len(all_games)))
# 根据所有可能的比分计算所有可能的积分榜
est_board = []
for possible_scores in all_possible_scores:
    new_board = copy.deepcopy(board)
    for i in range(len(all_games)):
        team1, team2 = all_games[i]
        score1, score2 = possible_scores[i]
        update_board(new_board, team1, team2, score1, score2)
    # 将当前积分榜按照积分、净胜分、胜场排序、字母顺序排序
    new_board = dict(sorted(new_board.items(), key=lambda x: (x[1][SCORE], x[1][NET_WIN], x[1][WIN]), reverse=True))
    est_board.append([possible_scores, new_board])

print("len(est_board):", len(est_board))
print("\n")

# 保存结果为pkl文件
# 保存积分榜
with open("est_board.pkl", "wb") as f:
    pickle.dump(est_board, f)
# 保存胜负关系
with open("win_lose.pkl", "wb") as f:
    pickle.dump(win_lose, f)
# 保存接下来的比赛
with open("next_game_play.pkl", "wb") as f:
    pickle.dump(all_games, f)

# 保存结果为txt文件
# 积分榜和胜负关系
with open("est_board_log.txt", "w") as f:
    # write current board and next game play
    f.write("当前积分榜:\n")
    f.write("战队\t胜 负 净胜分 积分\n")
    for team in board.keys():
        f.write(team + "\t" + str(board[team]))
        f.write("\n")
    f.write("胜负关系:\n")
    f.write(str(win_lose) + "\n")
    f.write("接下来的比赛:\n")
    for game in all_games:
        f.write(game[0] + " vs " + game[1])
        f.write("\n")
    # write estimated board
    f.write("所有可能的积分榜:\n")
    for tmp_board in est_board:
        f.write(str(tmp_board))
        f.write("\n")

# 保存结果，美化输出
with open("est_board_beautify.txt", "w") as f:
    # write current board and next game play
    f.write("当前积分榜:\n")
    f.write("{:<8} {:<9} {:<9} {:<9} {:<9}\n".format("战队", "胜", "负", "净胜分", "积分"))
    for team in board.keys():
        f.write("{:<10} {:<10} {:<10} {:<10} {:<10}\n".format(team, board[team][0], board[team][1], board[team][2], board[team][3]))
    f.write("胜负关系:\n")
    for win_team in win_lose.keys():
        f.write(win_team + " wins: " + str(win_lose[win_team]) + "\n")
    f.write("接下来的比赛:\n")
    for game in all_games:
        f.write("{:<5} vs. {:<5}\n".format(game[0], game[1]))
    # write estimated board
    f.write("\n\n\n")
    f.write("所有可能的积分榜:\n")
    for tmp_board in est_board:
        f.write("=====================================\n")
        f.write("比赛: " + str(all_games) + "\n")
        f.write("比分: " + str(tmp_board[0]) + "\n")
        f.write("{:<8} {:<9} {:<9} {:<9} {:<9}\n".format("战队", "胜", "负", "净胜分", "积分"))
        for team in tmp_board[1].keys():
            f.write("{:<10} {:<10} {:<10} {:<10} {:<10}\n".format(team, tmp_board[1][team][0], tmp_board[1][team][1], tmp_board[1][team][2], tmp_board[1][team][3]))
        f.write("\n")
