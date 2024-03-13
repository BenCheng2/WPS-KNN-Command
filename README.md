# WPS-KNN-Command
A simple Wifi Position System that takes input from the user and uses KNN to predict the user's current position.

## Functionality
Area.py: The object storing the area name and Accesspoints in the area.
GlobalVariables.py: The object storing the global variables.
MachineLearning.py: The object contains methods for loading data, training the model, and predicting the user's position.
Main.py: The main file that runs the program.

## The usage of the program
1. Git clone the project
2. Run the Main.py file
3. Input the area name and the index
4. Stop the program by typing "exit"
5. The program will output the predicted area name and the index of the user's current position.

## Example of usage
### Example of 'record' mode
Enter the command ('quit' to stop):  record
Enter the current area ('quit' to stop):  Room 1
Enter the current index: 1
Enter the current area ('quit' to stop):  Room 1
Enter the current index: 2
Enter the current area ('quit' to stop):  Room 1
Enter the current index: 3
Enter the current area ('quit' to stop):  Room 2
Enter the current index: 1
Enter the current area ('quit' to stop):  Room 2
Enter the current index: 2
Enter the current area ('quit' to stop):  Room 2
Enter the current index: 3
Enter the current area ('quit' to stop):  Room 3
Enter the current index: 1
Enter the current area ('quit' to stop):  quit

### Example of 'predict' mode
Enter the command ('quit' to stop):  predict
Room 1
