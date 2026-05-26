package Game.GuessTemplates;

import org.json.JSONObject;

import static Data.ADataHandler.jsonArrayToList;

import java.util.List;

public class ItemsGuessTemplate extends GuessTemplate{
    public String initial_release; // range
    public int stackable; // range
    public String rarity; // range
    public List<String> inventory_categories; // partial
    public String renewable; // binary
    public List<String> recipe; // partial
    public List<String> loot; // partial

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
    public int rarityCorrectness;
    public int creativeInventoryCategoryCorrectness;
    public int renewableCorrectness;
    public int recipeCorrectness;
    public int lootCorrectness;

    public ItemsGuessTemplate(String title, String release, int stackSize, String rarity,
                              List<String> inventory_categories, String renewable,
                              List<String> recipe, List<String> loot) {
        this.title = title;
        this.initial_release = release;
        this.stackable = stackSize;
        this.rarity = rarity;
        this.inventory_categories = inventory_categories;
        this.renewable = renewable;
        this.recipe = recipe;
        this.loot = loot;
    }

    public ItemsGuessTemplate() {
    }

    public static ItemsGuessTemplate validateItemGuess(ItemsGuessTemplate itemGuessToValidate, JSONObject solutionJSONObject) {
        // Binary: 0 = false, 1 = correct
        if (itemGuessToValidate.title.equals(solutionJSONObject.getString("title"))) {
            itemGuessToValidate.titleCorrectness = 1;
        } else {
            itemGuessToValidate.titleCorrectness = 0;
        }

        // Range (Version String comparison): 0 = lower, 1 = higher, 2 = correct
        int releaseComparison = compareReleaseVersions(itemGuessToValidate.initial_release, solutionJSONObject.getString("initial_release"));
        if(releaseComparison < 0) {
            itemGuessToValidate.releaseCorrectness = 0; // blockGuessToValidate has lower release version than solution
        } else if (releaseComparison > 0) {
            itemGuessToValidate.releaseCorrectness = 1; // blockGuessToValidate has higher release version than solution
        }
        else itemGuessToValidate.releaseCorrectness = 2; // correct release

        // Range (Integer): 0 = lower, 1 = higher, 2 = correct
        int targetStackSize = solutionJSONObject.getInt("stackable");
        if (itemGuessToValidate.stackable == targetStackSize) {
            itemGuessToValidate.stackSizeCorrectness = 2;
        } else if (itemGuessToValidate.stackable < targetStackSize) {
            itemGuessToValidate.stackSizeCorrectness = 0;
        } else {
            itemGuessToValidate.stackSizeCorrectness = 1;
        }

        // Range (Rarity Tier mapping): 0 = lower, 1 = higher, 2 = correct
        // Common = 0, Uncommon = 1, Rare = 2, Epic = 3
        java.util.List<String> rarities = java.util.Arrays.asList("common", "uncommon", "rare", "epic");
        int guessRarityWeight = rarities.indexOf(itemGuessToValidate.rarity.toLowerCase());
        int targetRarityWeight = rarities.indexOf(solutionJSONObject.getString("rarity").toLowerCase());

        if (guessRarityWeight == targetRarityWeight) {
            itemGuessToValidate.rarityCorrectness = 2;
        } else if (guessRarityWeight < targetRarityWeight) {
            itemGuessToValidate.rarityCorrectness = 0; // Guess tier is too low
        } else {
            itemGuessToValidate.rarityCorrectness = 1; // Guess tier is too high
        }

        // Partials: 0 = false, 1 = partial, 2 = correct
        List<String> targetCategories = jsonArrayToList(solutionJSONObject.getJSONArray("inventory_categories"));
        if (itemGuessToValidate.inventory_categories.equals(targetCategories)) {
            itemGuessToValidate.creativeInventoryCategoryCorrectness = 2;
        } else if (itemGuessToValidate.inventory_categories.stream().anyMatch(targetCategories::contains)) {
            itemGuessToValidate.creativeInventoryCategoryCorrectness = 1;
        } else {
            itemGuessToValidate.creativeInventoryCategoryCorrectness = 0;
        }

        // Partials: 0 = false, 1 = partial, 2 = correct
        // 1. Safely convert both the solution and guess to Strings
        String solutionStrRenewability = String.valueOf(solutionJSONObject.get("renewable")).trim();
        String guessStrRenewability = String.valueOf(itemGuessToValidate.renewable).trim();

        // 2. Evaluate the correctness levels
        if (guessStrRenewability.equalsIgnoreCase(solutionStrRenewability)) {
            // Exact match (e.g., both true, both false, or both "partial")
            itemGuessToValidate.renewableCorrectness = 2;
        } else if (guessStrRenewability.equalsIgnoreCase("partial") || solutionStrRenewability.equalsIgnoreCase("partial")) {
            // One is partial and the other is a strict true/false
            itemGuessToValidate.renewableCorrectness = 1;
        } else {
            // Complete mismatch (e.g., true vs false)
            itemGuessToValidate.renewableCorrectness = 0;
        }

        List<String> targetRecipe = jsonArrayToList(solutionJSONObject.getJSONArray("recipe"));
        if (itemGuessToValidate.recipe.equals(targetRecipe)) {
            itemGuessToValidate.recipeCorrectness = 2;
        } else if (itemGuessToValidate.recipe.stream().anyMatch(targetRecipe::contains)) {
            itemGuessToValidate.recipeCorrectness = 1;
        } else {
            itemGuessToValidate.recipeCorrectness = 0;
        }

        // Partials: 0 = false, 1 = partial, 2 = correct
        List<String> targetLoot = jsonArrayToList(solutionJSONObject.getJSONArray("loot"));
        if (itemGuessToValidate.loot.equals(targetLoot)) {
            itemGuessToValidate.lootCorrectness = 2;
        } else if (itemGuessToValidate.loot.stream().anyMatch(targetLoot::contains)) {
            itemGuessToValidate.lootCorrectness = 1;
        } else {
            itemGuessToValidate.lootCorrectness = 0;
        }

        return itemGuessToValidate;
    }

    /*
    docs or I go crazy:
    rarities:
    0 = common
    1 = uncommon
    2 = Rare
    3 = Epic

    categories:
    0 = ingredients
    1 = tools_and_utilities
    2 = redstone_blocks
    3 = functional_blocks
    4 = natural_blocks
    5 = combat
    6 = food_and_drinks
    7 = operator_utilities
    8 = spawn_eggs

    recipe:
    0 = crafting_table
    1 = none
    2 = furnace

    loot:
    0 = mob
    1 = fishing
    2 = trading
    3 = container
    4 = none
     */
}
