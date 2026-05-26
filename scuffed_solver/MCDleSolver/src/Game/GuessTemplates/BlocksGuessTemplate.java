package Game.GuessTemplates;

import org.json.JSONObject;

import static Data.ADataHandler.jsonArrayToList;

import java.util.List;

public class BlocksGuessTemplate extends GuessTemplate{
    public String initial_release; // range
    public int stackable; // range
    public List<String> tool; // partial
    public int blast_resistance; // range
    public int hardness; // range
    public String flammable; // binary
    public String full_block; // binary


    // correctness State
    // Range
    // 0 = lower, 1 = higher, 2 = correct

    // Binary
    // 0 = false, 1 = correct

    //Partials
    // 0 = false, 1 = partial, 2 = correct
    public int titleCorrectness;
    public int releaseCorrectness;
    public int stackSizeCorrectness;
    public int toolsCorrectness;
    public int blastResistanceCorrectness;
    public int hardnessCorrectness;
    public int flammableCorrectness;
    public int fullBlockCorrectness;

    public BlocksGuessTemplate(String title, String release, int stackSize, List<String> tools,
                               int blast_resistance, int hardness, String flammable, String fullBlock) {
        this.title = title;
        this.initial_release = release;
        this.stackable = stackSize;
        this.tool = tools;
        this.blast_resistance = blast_resistance;
        this.hardness = hardness;
        this.flammable = flammable;
        this.full_block = fullBlock;
    }

    public BlocksGuessTemplate() {
    }


    public static BlocksGuessTemplate validateBlockGuess(BlocksGuessTemplate blockGuessToValidate, JSONObject solutionJSONObject) {
        // Binary: 0 = false, 1 = correct
        if (blockGuessToValidate.title.equals(solutionJSONObject.getString("title"))) {
            blockGuessToValidate.titleCorrectness = 1;
        } else {
            blockGuessToValidate.titleCorrectness = 0;
        }

        // Range (Version String comparison): 0 = lower, 1 = higher, 2 = correct
        int releaseComparison = compareReleaseVersions(blockGuessToValidate.initial_release, solutionJSONObject.getString("initial_release"));
        if(releaseComparison < 0) {
            blockGuessToValidate.releaseCorrectness = 0; // blockGuessToValidate has lower release version than solution
        } else if (releaseComparison > 0) {
            blockGuessToValidate.releaseCorrectness = 1; // blockGuessToValidate has higher release version than solution
        }
        else blockGuessToValidate.releaseCorrectness = 2; // correct release

        // Range (Integer): 0 = lower, 1 = higher, 2 = correct
        int targetStackSize = solutionJSONObject.getInt("stackable");
        if (blockGuessToValidate.stackable == targetStackSize) {
            blockGuessToValidate.stackSizeCorrectness = 2;
        } else if (blockGuessToValidate.stackable < targetStackSize) {
            blockGuessToValidate.stackSizeCorrectness = 0;
        } else {
            blockGuessToValidate.stackSizeCorrectness = 1;
        }

        // Partials: 0 = false, 1 = partial, 2 = correct
        List<String> targetTools = jsonArrayToList(solutionJSONObject.getJSONArray("tool"));
        if (blockGuessToValidate.tool.equals(targetTools)) {
            blockGuessToValidate.toolsCorrectness = 2;
        } else if (blockGuessToValidate.tool.stream().anyMatch(targetTools::contains)) {
            blockGuessToValidate.toolsCorrectness = 1;
        } else {
            blockGuessToValidate.toolsCorrectness = 0;
        }

        // 1. Safely extract the solution value as a String to handle both booleans and text
        String solutionStrFlamability = String.valueOf(solutionJSONObject.get("flammable")).trim();
        String guessStrFlamability = String.valueOf(blockGuessToValidate.flammable).trim();

        // 2. Evaluate the correctness levels
        if (guessStrFlamability.equalsIgnoreCase(solutionStrFlamability)) {
            // Exact match (both are true, both are false, or both match the same string)
            blockGuessToValidate.flammableCorrectness = 2;
        } else if (guessStrFlamability.equalsIgnoreCase("partial") || solutionStrFlamability.equalsIgnoreCase("partial")) {
            // One of them is a partial match while the other is not
            blockGuessToValidate.flammableCorrectness = 1;
        } else {
            // Completely incorrect (e.g., true vs false)
            blockGuessToValidate.flammableCorrectness = 0;
        }

        // Range (Integer): 0 = lower, 1 = higher, 2 = correct
        int targetBlastResistance = solutionJSONObject.getInt("blast_resistance");
        if (blockGuessToValidate.blast_resistance == targetBlastResistance) {
            blockGuessToValidate.blastResistanceCorrectness = 2;
        } else if (blockGuessToValidate.blast_resistance < targetBlastResistance) {
            blockGuessToValidate.blastResistanceCorrectness = 0;
        } else {
            blockGuessToValidate.blastResistanceCorrectness = 1;
        }

        // Range (Integer): 0 = lower, 1 = higher, 2 = correct
        int targetHardness = solutionJSONObject.getInt("hardness");
        if (blockGuessToValidate.hardness == targetHardness) {
            blockGuessToValidate.hardnessCorrectness = 2;
        } else if (blockGuessToValidate.hardness < targetHardness) {
            blockGuessToValidate.hardnessCorrectness = 0;
        } else {
            blockGuessToValidate.hardnessCorrectness = 1;
        }

        // 1. Safely convert both the solution and guess to Strings
        String solutionStrFullBlock = String.valueOf(solutionJSONObject.get("full_block")).trim();
        String guessStrFullBlock = String.valueOf(blockGuessToValidate.full_block).trim();

        // 2. Evaluate the correctness levels
        if (guessStrFullBlock.equalsIgnoreCase(solutionStrFullBlock)) {
            // Exact match (e.g., both true, both false, or both "partial")
            blockGuessToValidate.fullBlockCorrectness = 2;
        } else if (guessStrFullBlock.equalsIgnoreCase("partial") || solutionStrFullBlock.equalsIgnoreCase("partial")) {
            // One is partial and the other is a strict true/false
            blockGuessToValidate.fullBlockCorrectness = 1;
        } else {
            // Complete mismatch (e.g., true vs false)
            blockGuessToValidate.fullBlockCorrectness = 0;
        }

        return blockGuessToValidate;
    }

    // DOCS BUT JUST ONE LINE THESE ARE THE TOOLS: any, pickaxe, hoe, shears, axe, none, sword, shovel
}
