package Solver;

import Game.GuessTemplates.*;
import org.json.JSONArray;
import org.json.JSONObject;
import java.util.*;

public class NextGuessComputer {

    private final JSONObject mapOfCategoryObjects;
    private final List<String> allEntityKeys;

    public static class CandidateEntropy {
        public String title;
        public double entropy;

        public CandidateEntropy(String title, double entropy) {
            this.title = title;
            this.entropy = entropy;
        }
    }

    public static class SolverResult {
        public List<CandidateEntropy> rankedCandidates;
        public int remainingCandidatesCount;

        public SolverResult(List<CandidateEntropy> rankedCandidates, int remainingCandidatesCount) {
            this.rankedCandidates = rankedCandidates;
            this.remainingCandidatesCount = remainingCandidatesCount;
        }
    }

    public NextGuessComputer(JSONObject mapOfCategoryObjects) {
        this.mapOfCategoryObjects = mapOfCategoryObjects;
        this.allEntityKeys = new ArrayList<>(mapOfCategoryObjects.keySet());
    }

    /**
     * Entry-point runner that dynamically computes entropy metrics matching your category context
     */
    public SolverResult calculateNextGuess(ArrayList<GuessTemplate> gameState, String category) {
        List<String> remainingCandidates = getRemainingCandidates(gameState, category);
        int remainingCount = remainingCandidates.size();

        List<CandidateEntropy> rankedList = new ArrayList<>();
        if (remainingCandidates.isEmpty()) {
            return new SolverResult(rankedList, 0);
        }

        Set<String> candidateSet = new HashSet<>(remainingCandidates);

        // Compute Expected Information Gain for all entries in the category
        for (String guessKey : allEntityKeys) {
            JSONObject guessJson = mapOfCategoryObjects.getJSONObject(guessKey);
            Map<String, Integer> patternCounts = new HashMap<>();

            for (String candidateKey : remainingCandidates) {
                JSONObject candidateJson = mapOfCategoryObjects.getJSONObject(candidateKey);

                // processing based on active game rules
                GuessTemplate simulatedResult = simulateValidation(guessKey, guessJson, candidateJson, category);
                String patternSignature = getPatternSignature(simulatedResult, category);

                patternCounts.put(patternSignature, patternCounts.getOrDefault(patternSignature, 0) + 1);
            }

            double entropy = 0.0;
            double totalCandidates = remainingCandidates.size();
            for (int count : patternCounts.values()) {
                double pr = count / totalCandidates;
                entropy -= pr * (Math.log(pr) / Math.log(2));
            }

            rankedList.add(new CandidateEntropy(guessKey, entropy));
        }

        // Apply smart sorting with candidate priority tie-breakers
        rankedList.sort((a, b) -> {
            int cmp = Double.compare(b.entropy, a.entropy);
            if (cmp != 0) return cmp;

            boolean aIsValidCandidate = candidateSet.contains(a.title);
            boolean bIsValidCandidate = candidateSet.contains(b.title);

            if (aIsValidCandidate && !bIsValidCandidate) return -1;
            if (!aIsValidCandidate && bIsValidCandidate) return 1;

            return a.title.compareTo(b.title);
        });

        return new SolverResult(rankedList, remainingCount);
    }

    private List<String> getRemainingCandidates(ArrayList<GuessTemplate> gameState, String category) {
        List<String> candidates = new ArrayList<>(allEntityKeys);

        for (GuessTemplate historicalGuess : gameState) {
            String historicalPattern = getPatternSignature(historicalGuess, category);
            String targetTitle = getGuessTitle(historicalGuess, category);
            JSONObject historicalGuessJson = mapOfCategoryObjects.getJSONObject(targetTitle);

            // Extract whether this historical attempt was the exact correct match
            boolean isGuessCorrect = switch (category.toLowerCase()) {
                case "mobs" -> ((MobsGuessTemplate) historicalGuess).titleCorrectness == 1;
                case "blocks" -> ((BlocksGuessTemplate) historicalGuess).titleCorrectness == 1;
                case "items" -> ((ItemsGuessTemplate) historicalGuess).titleCorrectness == 1;
                default -> false;
            };

            List<String> filteredCandidates = new ArrayList<>();
            for (String candidateKey : candidates) {

                // EXPLICIT AMBIGUITY OVERRIDE: If the guess was incorrect,
                // it cannot be the solution candidate. Prune it immediately.
                if (!isGuessCorrect && candidateKey.equals(targetTitle)) {
                    continue;
                }

                JSONObject candidateJson = mapOfCategoryObjects.getJSONObject(candidateKey);
                GuessTemplate simulatedResult = simulateValidation(targetTitle, historicalGuessJson, candidateJson, category);

                if (getPatternSignature(simulatedResult, category).equals(historicalPattern)) {
                    filteredCandidates.add(candidateKey);
                }
            }
            candidates = filteredCandidates;
        }
        return candidates;
    }

    private GuessTemplate simulateValidation(String guessKey, JSONObject guessJson, JSONObject candidateJson, String category) {
        switch (category.toLowerCase()) {
            case "mobs" -> {
                MobsGuessTemplate dummy = createMobTemplate(guessKey, guessJson);
                return MobsGuessTemplate.validateMobGuess(dummy, candidateJson);
            }
            case "blocks" -> {
                BlocksGuessTemplate dummy = createBlockTemplate(guessKey, guessJson);
                return BlocksGuessTemplate.validateBlockGuess(dummy, candidateJson);
            }
            case "items" -> {
                ItemsGuessTemplate dummy = createItemTemplate(guessKey, guessJson);
                return ItemsGuessTemplate.validateItemGuess(dummy, candidateJson);
            }
            default -> throw new IllegalArgumentException("Unknown context type: " + category);
        }
    }

    private String getPatternSignature(GuessTemplate template, String category) {
        switch (category.toLowerCase()) {
            case "mobs" -> {
                MobsGuessTemplate mob = (MobsGuessTemplate) template;
                return mob.titleCorrectness + "," + mob.releaseCorrectness + "," + mob.healthCorrectness + "," +
                        mob.heightCorrectness + "," + mob.behaviourCorrectness + "," + mob.spawnCorrectness + "," + mob.classificationCorrectness;
            }
            case "blocks" -> {
                BlocksGuessTemplate b = (BlocksGuessTemplate) template;
                return b.titleCorrectness + "," + b.releaseCorrectness + "," + b.stackSizeCorrectness + "," +
                        b.toolsCorrectness + "," + b.blastResistanceCorrectness + "," + b.hardnessCorrectness + "," +
                        b.flammableCorrectness + "," + b.fullBlockCorrectness;
            }
            case "items" -> {
                ItemsGuessTemplate item = (ItemsGuessTemplate) template;
                return item.titleCorrectness + "," + item.releaseCorrectness + "," + item.stackSizeCorrectness + "," +
                        item.rarityCorrectness + "," + item.creativeInventoryCategoryCorrectness + "," +
                        item.renewableCorrectness + "," + item.recipeCorrectness + "," + item.lootCorrectness;
            }
            default -> {
                return "";
            }
        }
    }

    private String getGuessTitle(GuessTemplate template, String category) {
        return switch (category.toLowerCase()) {
            case "mobs" -> ((MobsGuessTemplate) template).title;
            case "blocks" -> ((BlocksGuessTemplate) template).title;
            case "items" -> ((ItemsGuessTemplate) template).title;
            default -> "";
        };
    }

    // Factory helper methods to generate clean starting states from JSON
    private MobsGuessTemplate createMobTemplate(String title, JSONObject json) {
        return new MobsGuessTemplate(
                title,
                json.getString("initial_release"),
                json.getDouble("health"),
                json.getDouble("height"),
                jsonArrayToList(json.getJSONArray("behavior")),
                jsonArrayToList(json.getJSONArray("spawn")),
                jsonArrayToList(json.getJSONArray("classification"))
        );
    }

    private BlocksGuessTemplate createBlockTemplate(String title, JSONObject json) {
        return new BlocksGuessTemplate(
                title,
                json.getString("initial_release"),
                json.getInt("stackable"),
                jsonArrayToList(json.getJSONArray("tool")),
                json.getInt("blast_resistance"),
                json.getInt("hardness"),
                String.valueOf(json.get("flammable")),
                String.valueOf(json.get("full_block"))
        );
    }

    private ItemsGuessTemplate createItemTemplate(String title, JSONObject json) {
        return new ItemsGuessTemplate(
                title,
                json.getString("initial_release"),
                json.getInt("stackable"),
                json.getString("rarity"),
                jsonArrayToList(json.getJSONArray("inventory_categories")),
                String.valueOf(json.get("renewable")),
                jsonArrayToList(json.getJSONArray("recipe")),
                jsonArrayToList(json.getJSONArray("loot"))
        );
    }

    private List<String> jsonArrayToList(JSONArray array) {
        List<String> list = new ArrayList<>();
        for (int i = 0; i < array.length(); i++) {
            list.add(array.getString(i));
        }
        return list;
    }

    public static void printAllEntropyOfCurrentGameState(SolverResult curResult) {
        int number = 1;
        for(CandidateEntropy candiate : curResult.rankedCandidates) {
            System.out.println("Number: " + number + "   Titel: " + candiate.title +  "    Entropy:  " + candiate.entropy);
            number++;
        }
        System.out.println("------------------------------------------------------------------------");
        System.out.println("------------------------------------------------------------------------");
    }
}