from GlobalVariable import KNN_Model

PAST_LENGTH = 0


def predict_knn(X, y, current):
    """
    Predict the current area using the KNN model
    :param current:
    :return:
    """
    global PAST_LENGTH

    if len(X) != PAST_LENGTH:
        KNN_Model.fit(X, y)
        PAST_LENGTH = len(X)

    result = KNN_Model.predict([current])
    return result[0]