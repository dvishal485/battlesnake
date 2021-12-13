import numpy as np
from random import choice


def global_variables(mode: str = "default"):
    '''
    This functions gives information on the gain and
    loss behaviour for the battlesnake. Eg. - The gain
    it will be having by eating a food item or the loss
    it will be having if it hits other snake etc.
    '''
    food_val = 3
    corner_val = -1
    food_surr_val = 2
    other_snake_damage_val = 400
    impossible = 2000
    prioritize_food_row = False
    prioritize_food_col = False
    if(mode == "survival"):
        prioritize_food_row = True
        prioritize_food_col = True
        corner_val = -2
        food_val = 4
        food_surr_val = 3
    return (food_val, corner_val, food_surr_val, other_snake_damage_val, impossible, prioritize_food_row, prioritize_food_col)


def generate_smart_move(data: dict, mode: str = "default") -> str:
    '''
    Generates the smartest move by identifying the
    move with maximum profit ( or minimum loss ) by
    evaluating the board
    '''
    food_val, corner_val, food_surr_val, other_snake_damage_val, impossible, prioritize_food_row, prioritize_food_col = global_variables(
        mode)
    height = data["board"]["height"]
    width = data["board"]["width"]
    food = data["board"]["food"]
    hazards = data["board"]["hazards"]
    snakes = data["board"]["snakes"]
    you = data["you"]
    # Build board function builds a board matrix with all the given information
    board = build_board(height, width, food, hazards, snakes, you, mode)
    # log the board matrix
    print(board.astype('int'))
    # classify invalid move as an impossible move by making its value highly negative
    # the value is stored in global variable as "impossible"
    x = you["head"]["x"]
    y = you["head"]["y"]
    # get the 3x3 matrix around the head
    surr = surrSq(x, y, board)
    print(f"\nSurrounding 3x3 board :\n{surr}")
    surr[0][0] = - impossible
    surr[2][0] = -impossible
    surr[1][1] = -impossible
    surr[0][2] = -impossible
    surr[2][2] = -impossible
    # predict the moves with maximum profit/minimum loss
    # ( move with most +ve value in the 3x3 matrix )
    result = np.where(surr == np.amax(surr))
    possibleMoves = []
    listOfCordinates = list(zip(result[0], result[1]))
    # initialize "future" variable caz we will be predicting future
    # Note : No ML/AI used, predicting future basically means
    # predicting the next best move and identify if it's
    # in our battlesnake's favour or not

    def surrMatrixMean(arr, value=-1700):
        '''
        Returns the mean of surrounding matrix excluding the outbounds
        '''
        return np.nanmean(np.where(arr == value, np.nan, arr))

    future = []
    superFuture = []
    for cord in listOfCordinates:
        if cord == (0, 1):
            possibleMoves.append("up")
            you["head"] = {"x": x, "y": y+1}
            you["body"].append({"x": x, "y": y+1})
            board = build_board(height, width, food,
                                hazards, snakes, you, mode)
            if(y != height-1):
                futureSurr = surrSq(x, y+1, board)
            else:
                futureSurr = surrSq(x, y, board)
            future.append(np.amax(futureSurr))
            superFuture.append(surrMatrixMean(futureSurr))
        elif cord == (1, 2):
            you["head"] = {"x": x+1, "y": y}
            you["body"].append({"x": x+1, "y": y})
            board = build_board(height, width, food,
                                hazards, snakes, you, mode)
            possibleMoves.append("right")
            if(x != width-1):
                futureSurr = surrSq(x+1, y, board)
            else:
                futureSurr = surrSq(x, y, board)
            future.append(np.amax(futureSurr))
            superFuture.append(surrMatrixMean(futureSurr))
        elif cord == (1, 0):
            you["head"] = {"x": x-1, "y": y}
            you["body"].append({"x": x-1, "y": y})
            board = build_board(height, width, food,
                                hazards, snakes, you, mode)
            possibleMoves.append("left")
            if x != 0:
                futureSurr = surrSq(x-1, y, board)
            else:
                futureSurr = surrSq(x-1, y, board)
            future.append(np.amax(futureSurr))
            superFuture.append(surrMatrixMean(futureSurr))
        elif cord == (2, 1):
            you["head"] = {"x": x, "y": y-1}
            you["body"].append({"x": x, "y": y-1})
            board = build_board(height, width, food,
                                hazards, snakes, you, mode)
            possibleMoves.append("down")
            if y != 0:
                futureSurr = surrSq(x, y-1, board)
            else:
                futureSurr = surrSq(x, y, board)
            future.append(np.amax(futureSurr))
            superFuture.append(surrMatrixMean(futureSurr))
    try:
        # Predicting self future
        future = np.array(future)
        indices = np.array(np.where(future == np.amax(future)))
        priority = []
        for i in indices[0]:
            i = int(i)
            pM = possibleMoves[i]
            priority.append(pM)
        possibleMoves = priority
    except:
        # never encountered this but just in case...
        print("Sad things happened while predicting future!")
    finally:
        # After predicting the future predict the super-future
        # to reduce the degree of randomness! super-future is
        # just a name I made up for predicting a better future
        try:
            indices = np.array(np.where(superFuture == np.amax(superFuture)))
            superPriority = []
            for i in indices:
                i = int(i)
                pM = possibleMoves[i]
                superPriority.append(pM)
            possibleMoves = superPriority
            print(
                f"Future Prediction : {priority}\nSuperFuture Prediction : {superPriority}")
        except:
            print("Sad things happened while predicting super future!!")
        move = choice(possibleMoves)
        print(f"Moving {move}!")
        return move


def surrSq(x: int, y: int, board):
    '''
    Gets the surrounding 3x3 board around the given
    coordinate (x, y)
    '''
    y = board.shape[1]-1-y
    fakeError = "This is not an error, but I'm just taking advantage of errors!"
    arr = np.full(shape=(3, 3), fill_value=-1700)
    # make sure indices are non negative as they will
    # result to the some value accoridngly but I want
    # to declare those entry as invalid
    try:
        if(y-1 < 0 or x-1 < 0):
            raise fakeError
        f1 = board[y-1][x-1]
    except:
        f1 = -1700

    try:
        if(y < 0 or x-1 < 0):
            raise fakeError
        f2 = board[y][x-1]
    except:
        f2 = -1700

    try:
        if(y+1 < 0 or x-1 < 0):
            raise fakeError
        f3 = board[y+1][x-1]
    except:
        f3 = -1700

    try:
        if(y-1 < 0 or x < 0):
            raise fakeError
        g1 = board[y-1][x]
    except:
        g1 = -1700

    try:
        if(y < 0 or x < 0):
            raise fakeError
        g2 = board[y][x]
    except:
        g2 = -1700

    try:
        if(y+1 < 0 or x < 0):
            raise fakeError
        g3 = board[y+1][x]
    except:
        g3 = -1700

    try:
        if(y-1 < 0 or x+1 < 0):
            raise fakeError
        h1 = board[y-1][x+1]
    except:
        h1 = -1700

    try:
        if(y < 0 or x+1 < 0):
            raise fakeError
        h2 = board[y][x+1]
    except:
        h2 = -1700

    try:
        if(y+1 < 0 or x+1 < 0):
            raise fakeError
        h3 = board[y+1][x+1]
    except:
        h3 = -1700
    # finally create the 3x3 matrix and return
    arr = np.array([
        [f1, f2, f3, ],
        [g1, g2, g3, ],
        [h1, h2, h3, ]]).T

    return arr.astype('int')


def build_board(height, width, food, hazards, snakes, you, mode):
    '''
    Takes in the information about the game and
    generates a matrix ( numpy array ) for the
    board containg the gain and loss information
    at every point
    '''
    food_val, corner_val, food_surr_val, other_snake_damage_val, impossible, prioritize_food_row, prioritize_food_col = global_variables(
        mode)
    board = np.ones((height, width))
    # remove edges from priority by lowering it's gain value
    board[0][:] = corner_val
    board[:][height-1] = corner_val
    for i in range(height):
        board[i][0] = corner_val
        board[i][width-1] = corner_val
    for i in food:
        board[height - 1 - i["y"], i["x"]] += food_val
        try:
            board[height-1-i["y"]+1, i["x"]] += food_surr_val
        except:
            None
        try:
            board[height-1-i["y"]-1, i["x"]] += food_surr_val
        except:
            None
        try:
            board[height-1-i["y"], i["x"]+1] += food_surr_val
        except:
            None
        try:
            board[height-1-i["y"]+1, i["x"]+1] += food_surr_val
        except:
            None
        try:
            board[height-1-i["y"]-1, i["x"]+1] += food_surr_val
        except:
            None
        try:
            board[height-1-i["y"]-1, i["x"]-1] += food_surr_val
        except:
            None
        try:
            board[height-1-i["y"], i["x"]-1] += food_surr_val
        except:
            None
        try:
            board[height-1-i["y"]+1, i["x"]-1] += food_surr_val
        except:
            None
        try:
            board[height-1-i["y"], i["x"]] += food_surr_val
        except:
            None
        if prioritize_food_col:
            try:
                for x in range(width):
                    try:
                        board[i["y"]][x] += food_surr_val-1
                    except:
                        print(f"Failed to prioritize ({x, i['y']})")
            except:
                print("Failed to prioritize food column")
        if prioritize_food_row:
            try:
                for y in range(height):
                    try:
                        board[y][i["x"]] += food_surr_val-1
                    except:
                        print(f"Failed to prioritize ({i['x'], y})")
            except:
                print("Failed to prioritize food row")
    for i in hazards:
        board[height - 1 - i["y"], i["x"]] -= food_val
    for snake in snakes:
        # snake's head can be a potential danger in near future!
        try:
            board[height-1-snake["head"]["y"]+1,
                  snake["head"]["x"]] -= food_val
        except:
            None
        try:
            board[height-1-snake["head"]["y"]-1,
                  snake["head"]["x"]] -= food_val
        except:
            None
        try:
            board[height-1-snake["head"]["y"],
                  snake["head"]["x"]+1] -= food_val
        except:
            None
        try:
            board[height-1-snake["head"]["y"],
                  snake["head"]["x"]-1] -= food_val
        except:
            None
        for i in snake["body"]:
            board[height-1 - i["y"], i["x"]] -= other_snake_damage_val * 2.5
            try:
                board[height-1 - i["y"]+1, i["x"]] -= food_val-1
            except:
                None
            try:
                board[height-1 - i["y"]-1, i["x"]] -= food_val-1
            except:
                None
            try:
                board[height-1 - i["y"], i["x"]+1] -= food_val-1
            except:
                None
            try:
                board[height-1 - i["y"], i["x"]-1] -= food_val-1
            except:
                None
    for i in you["body"]:
        board[height-1 - i["y"], i["x"]] -= other_snake_damage_val+100
    return board
