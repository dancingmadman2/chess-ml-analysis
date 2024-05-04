# Chess ML Analysis

## Overview
This repository hosts a machine learning project aimed at predicting the outcomes of chess games. It explores various statistical and machine learning techniques to analyze chess strategies and tactics derived from games played by the Stockfish chess engine against itself under diverse configurations.

## Project Structure

- **dataset_generator.py**: Generates the dataset using the Stockfish engine and an opening book to diversify game strategies.
- **data_prep.py**: Contains scripts for preprocessing the dataset such as handling missing values, encoding categorical features, and scaling.
- **model_operations.py**: Implements several machine learning models (Random Forest, Logistic Regression, SVM, Naive Bayes) and includes functions for training, predicting, and evaluating these models.
- **main.py**: The main script that integrates data loading, preprocessing, model training, evaluation, and visual reporting.

## Features

The dataset captures various aspects of chess games, including:
- **Piece Activity**: Effectiveness of piece placement and board control.
- **Castling**: Defensive strategies indicated by castling moves.
- **Control of Center**: Control over central squares which is a critical aspect of chess strategy.
- **Piece Composition**: The ratio of knights to bishops, analyzing their value based on the game state.
- **Engine Skill**: Randomized skill levels to generate diverse game strategies and outcomes.
- **Total Moves**: Total number of moves played in the game.
- **Openings**: Categorized opening moves from the games.
- **Evaluation after Move 15**: Stockfish engine's board evaluation after 15 moves.
- **Sacrifices**: Strategic sacrifices made by each player.

## Installation

To run the chess analysis, you'll need the Stockfish engine.Download it from the official Stockfish website:
[Download Stockfish](https://stockfishchess.org/download/)

Ensure Python 3.x is installed along with the following libraries:<br>
```bash
pip install python-chess pandas scikit-learn matplotlib seaborn imbalanced-learn
```
## Usage

Generate the dataset and run preprocessing and model training: <br>
```bash
python dataset_generator.py
```
```bash
python main.py
```

## Results
These results were obtained using a Random Forest model with a 75-25 training-test split on a dataset consisting of 2,500 entries.
<img src="https://github.com/dancingmadman2/chess-ml-analysis/assets/88443368/48e80265-874a-4912-9bed-389235635b5f" width=40% >
<img src="https://github.com/dancingmadman2/chess-ml-analysis/assets/88443368/4cdf27b7-6933-46fa-9976-183323239f06" width=40% >
<img src="https://github.com/dancingmadman2/chess-ml-analysis/assets/88443368/4513a4af-5ba2-4854-b9cb-38c8b57cf85e" height=33%>



