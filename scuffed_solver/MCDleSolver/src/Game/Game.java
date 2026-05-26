package Game;

import Game.Simulator.*;
import Data.ADataHandler;
import Solver.NextGuessComputer;

import Game.GuessTemplates.*;

import java.io.IOException;
import java.util.Scanner;

public class Game {

    private final String accessMode;
    private final String categoryBeingPlayed;
    private String solution;

    private final ADataHandler gameDataHandler;
    private  GameStateTracker gameStateTracker = null;
    private final NextGuessComputer nextGuessComputer;

    private final Scanner inputScanner = new Scanner(System.in);
    private Visualizer visualizer;

    public Game(String accessMode, String categoryBeingPlayed) throws IOException {
        this.accessMode = accessMode;
        this.categoryBeingPlayed = categoryBeingPlayed;

        gameDataHandler = new ADataHandler(accessMode, categoryBeingPlayed);

        this.nextGuessComputer = new NextGuessComputer(gameDataHandler.getJsonCategoryObject());

        switch (accessMode) {
            case "random" -> {
                solution = gameDataHandler.generateRandomSolution();
                gameStateTracker = new GameStateTracker(categoryBeingPlayed, solution, gameDataHandler.getJsonCategoryObject());
                this.visualizer = new Visualizer();

                System.out.println("Random solution has been generated");
                System.out.println("Set Solution to Random, this time it is " + solution);

                startRandomGame();
            }
            case "testing" -> {
                System.out.println("Don't forget to set a solution before commencing testing, there is NO default value");
                System.out.println("type guess to test against now! ");
                String customGuess = inputScanner.next();
                int index = 0;
                for(int i = 0; i < gameDataHandler.getOriginalKeySetSizeOfMapOfCategoryObjects(); i++){
                    if(gameDataHandler.getArrayListCorrespondingToCategoryEntityKeys().get(i).equals(customGuess)){
                        index = i;
                        break;
                    }
                }
                setSolution(gameDataHandler.getArrayListCorrespondingToCategoryEntityKeys().get(index));
                this.visualizer = new Visualizer();
                gameStateTracker = new GameStateTracker(categoryBeingPlayed, solution, gameDataHandler.getJsonCategoryObject());
                startTesting();
            }
            case "simulating" -> {
                System.out.println("Starting Simulation");
                gameStateTracker = new GameStateTracker(categoryBeingPlayed, gameDataHandler.getJsonCategoryObject());
                startSimulation();
            }
            case "manualVerification" -> {
                System.out.println("Starting manual verification");
                gameStateTracker = new GameStateTracker(categoryBeingPlayed, gameDataHandler.getJsonCategoryObject());
                gameStateTracker.setManualVerification(true);
                this.visualizer = new Visualizer();

            }
            default -> throw new IllegalArgumentException("not a valid accessMode category in Game constructor");
        }
    }

    public void startManuallVerificationGame(){
        boolean solutionFound = false;
        int guessCount = 0;
        while(!solutionFound){
            GuessTemplate currentUserGuess = manualGuess();
            guessCount++;
            System.out.println("UNDER DEVELOPMENT DOES NOT WORK AND WILL NOT DO ANYTHING");
            solutionFound = true;
        }
    }

    public void startSimulation() throws IOException {
        System.out.println("NOTHING to see here, still in development!");
        Simulator simulator = new Simulator(this);
        simulator.simulate();
        Simulator.GuessScore bestScore = simulator.getBestScore();
        System.out.println(" the best first guess is: " + bestScore.title +
                           "with an average score of: " + bestScore.averageScore);

        simulator.createVisualisation();
    }

    public void startTesting() {
        visualizer.displayMessage("=== Starting Testing Mode ===");
        if (solution == null || solution.isEmpty()) {
            gameStateTracker.setSolution(solution);
            visualizer.displayMessage("Testing with: " + solution);
        }
        startRandomGame();
    }

    public void startRandomGame() {
        boolean solutionFound = false;
        int guessCount = 0;
        while (!solutionFound) {
            GuessTemplate currentUserGuess = manualGuess();
            guessCount++;
            switch (categoryBeingPlayed.toLowerCase()) {
                case "mobs" -> {
                    if (((MobsGuessTemplate) currentUserGuess).title.equals(solution)) solutionFound = true;
                }
                case "blocks" -> {
                    if (((BlocksGuessTemplate) currentUserGuess).title.equals(solution)) solutionFound = true;
                }
                case "items" -> {
                    if (((ItemsGuessTemplate) currentUserGuess).title.equals(solution)) solutionFound = true;
                }
            }
        }
        System.out.println();
        System.out.println("Correct!!! You've won the game!");

        visualizer.displayVictory(solution, guessCount);
    }

    public GuessTemplate manualGuess() {
        // Runs dynamic-multi-category live analysis immediately at the start of your turn
        visualizer.displayMessage("📊 Analyzing database to calculate optimal choices...");
        NextGuessComputer.SolverResult result = nextGuessComputer.calculateNextGuess(
                gameStateTracker.getGameState(),
                categoryBeingPlayed
        );

        if (result != null) {
            visualizer.displaySolverAnalysis(result.rankedCandidates, result.remainingCandidatesCount);
            NextGuessComputer.printAllEntropyOfCurrentGameState(result);
        }

        String userGuess = "";
        visualizer.displayMessage("Awaiting your guess...");

        do {
            userGuess = visualizer.getUserInput();

            if (!gameDataHandler.getArrayListCorrespondingToCategoryEntityKeys().contains(userGuess)) {
                visualizer.displayMessage("Invalid entity! '" + userGuess + "' is not in the database. Try again.");
            }
        } while (!gameDataHandler.getArrayListCorrespondingToCategoryEntityKeys().contains(userGuess));

        visualizer.displayMessage("Valid guess accepted!");

        GuessTemplate newGuess = gameStateTracker.generateGuess(userGuess, gameDataHandler.getJsonCategoryObject().getJSONObject(userGuess));
        gameStateTracker.setNewGamestate(newGuess);

        visualizer.displayGuessResult(userGuess, newGuess);

        return newGuess;
    }

    public void automatedTestingGuess(GuessTemplate newGuess) {
    }

    public String getAccessMode() {
        return accessMode;
    }

    public String getCategoryBeingPlayed() {
        return categoryBeingPlayed;
    }
    public ADataHandler getGameDataHandler(){
        return gameDataHandler;
    }

    public GameStateTracker getGameStateTracker() {
        return gameStateTracker;
    }

    public void setSolution(String solution) {
        this.solution = solution;
    }

    public NextGuessComputer getNextGuessComputer() {
        return nextGuessComputer;
    }
}