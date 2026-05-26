package Game;

import Game.GuessTemplates.*;
import org.json.JSONObject;

import java.util.*;

import static Data.ADataHandler.jsonArrayToList;
import static Game.GuessTemplates.BlocksGuessTemplate.validateBlockGuess;
import static Game.GuessTemplates.ItemsGuessTemplate.validateItemGuess;
import static Game.GuessTemplates.MobsGuessTemplate.validateMobGuess;

public class GameStateTracker {
    // Stores all states associated with the current game
    // Every array List inside gameState represents an individual guess
    // Meanings and assumed size of Entries

    // Size (number of entries):
    // mobs 7
    // items 8
    // blocks 8

    private final String categoryBeingPlayed; // blocks, mobs, items
    private String solution;
    private JSONObject solutionJSONObject;
    private  List<String> categoryBeingPlayedCategoriesList;
    private  JSONObject mapOfCategoryObjects;

    private ArrayList<GuessTemplate> gameState;
    private  int gameStateInternalArrayListSize;
    boolean manualVerification = false;

    // constructor for random mode
    public GameStateTracker(String categoryBeingPlayed, String solution, JSONObject mapOfCategoryObjects) {
        // initialization of fundamental fields
        this.categoryBeingPlayed = categoryBeingPlayed;
        this.solution = solution;
        this.solutionJSONObject = mapOfCategoryObjects.getJSONObject(solution);
        this.mapOfCategoryObjects = mapOfCategoryObjects;
        gameState = new ArrayList<>();

        determineCategoriesForGameStateTracking();
    }

    // constructor for simulation mode
    public GameStateTracker(String categoryBeingPlayed, JSONObject mapOfCategoryObjects) {
        // initialization of fundamental fields
        this.categoryBeingPlayed = categoryBeingPlayed;
        this.mapOfCategoryObjects = mapOfCategoryObjects;
        gameState = new ArrayList<>();

        determineCategoriesForGameStateTracking();
    }

    public void determineCategoriesForGameStateTracking(){
        // determine number of categories for gameState tracking
        switch (categoryBeingPlayed) {
            case "mobs" -> {
                gameStateInternalArrayListSize = 7;
                categoryBeingPlayedCategoriesList = Arrays.asList("title", "initial_release", "health", "height", "behaviour", "spawn", "classification");
            }
            case "items" -> {
                gameStateInternalArrayListSize = 8;
                categoryBeingPlayedCategoriesList = Arrays.asList("title", "initial_release", "stackable", "rarity", "inventory_categories", "renewable", "recipe", "loot");
            }
            case "blocks" ->{
                gameStateInternalArrayListSize = 8;
                categoryBeingPlayedCategoriesList = Arrays.asList("title", "initial_release", "stackable", "tool", "blast_resistance", "hardness", "fire_catch", "full_block");
            }
            default -> throw new IllegalArgumentException("Not a valid category for game state tracking");
        }
    }

    // method to generate a new guess according to template of category played
    // and directly validates the guess
    public GuessTemplate generateGuess(String guess, JSONObject guessJSONObject) {

        return switch (categoryBeingPlayed) {
            case "mobs" -> validateGuess(createMobGuess(guess, guessJSONObject));
            case "blocks" -> validateGuess(createBlockGuess(guess, guessJSONObject));
            case "items" -> validateGuess(createItemGuess(guess, guessJSONObject));
            default -> throw new IllegalArgumentException();
        };
    }

    public GuessTemplate validateGuess(GuessTemplate guessToValidate){
        switch (categoryBeingPlayed) {
            case ("mobs") -> {
                return validateMobGuess((MobsGuessTemplate) guessToValidate, solutionJSONObject);
            }
            case ("items") -> {
                return validateItemGuess((ItemsGuessTemplate) guessToValidate, solutionJSONObject);
            }
            case("blocks") -> {
                return validateBlockGuess((BlocksGuessTemplate) guessToValidate, solutionJSONObject);
            }
            default -> throw new IllegalArgumentException("Not a valid category for game state tracking");
        }
    }

    public GuessTemplate createMobGuess(String title, JSONObject jsonObject) {
        String release = jsonObject.getString("initial_release");
        int health = jsonObject.getInt("health");

        // height in json is decimal -> use double
        double height = jsonObject.getDouble("height");

        List<String> behaviour = jsonArrayToList(jsonObject.getJSONArray("behavior"));

        List<String> spawn = jsonArrayToList(jsonObject.getJSONArray("spawn"));

        List<String> classification = jsonArrayToList(jsonObject.getJSONArray("classification"));

        return new MobsGuessTemplate(
                title,
                release,
                health,
                height,
                behaviour,
                spawn,
                classification
        );

    }
    public GuessTemplate createBlockGuess(String title, JSONObject jsonObject){
        String release = jsonObject.getString("initial_release");
        int stackSize = jsonObject.getInt("stackable");

        List<String> tool = jsonArrayToList(jsonObject.getJSONArray("tool"));

        int blastResistance = jsonObject.getInt("blast_resistance");
        int hardness = jsonObject.getInt("hardness");
        String flammable = String.valueOf(jsonObject.get("flammable"));
        String fullBlock = String.valueOf(jsonObject.get("full_block"));

        return new BlocksGuessTemplate(
                title,
                release,
                stackSize,
                tool,
                blastResistance,
                hardness,
                flammable,
                fullBlock
        );

    }

    public GuessTemplate createItemGuess(String title, JSONObject jsonObject){
        String renewable =
                String.valueOf(jsonObject.get("renewable"));

        int stackSize =
                jsonObject.getInt("stackable");

        String rarity =
                jsonObject.getString("rarity");

        String release =
                jsonObject.getString("initial_release");

        List<String> recipe = jsonArrayToList(jsonObject.getJSONArray("recipe"));

        List<String> loot = jsonArrayToList(jsonObject.getJSONArray("loot"));

        List<String> inventoryCategories = jsonArrayToList(jsonObject.getJSONArray("inventory_categories"));

        return new ItemsGuessTemplate(
                title,
                release,
                stackSize,
                rarity,
                inventoryCategories,
                renewable,
                recipe,
                loot
        );

    }

    public void setNewGamestate(GuessTemplate newGuess) {
        // updates the gamestate based on the provided guess
        gameState.add((GuessTemplate) newGuess);
    }

    // util functions

    public void clearGameState(){
        // resets game state array to an empty one
        gameState.clear();
    }

    public ArrayList<GuessTemplate> getGameState() {
        return gameState;
    }

    public void setSolution(String newSolution){
        solution = newSolution;
    }

    public void setSolutionJSONObject(JSONObject solutionJSONObject) {
        this.solutionJSONObject = solutionJSONObject;
    }

    public boolean solutionFound(){
        String titleOfLastGuess = this.gameState.getLast().title;
        return (titleOfLastGuess.equals(solution));
    }

    public void setManualVerification(boolean newState) {
        manualVerification = newState;
    }
}
