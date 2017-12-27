
def give_score(user, game_type, score=1):
    if score == -1:
        user.user_stat[game_type][1] += 1
    else:
        user.user_stat[game_type][0] += score
    if (user.user_stat[game_type][1] > 10)\
            and (user.user_stat[game_type][0] / user.user_stat[game_type][1] > 0.5) and (user.user_rights == 1):
        user.user_rights = 2
    elif user.user_rights == 2:
        user.user_rights = 1
    user.temp.db_save_all()
