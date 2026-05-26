package Data;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.*;

public class ADataHandler {

    private String datasetUsed = "original";
    private final String accessMode; // random, testing
    private final String categoryBeingPlayed; // blocks, mobs, items
    private final String JSONFilePath; // filePath to json of categoryBeingPlayed
    private String JSONFileContentAsString; // contents of JSON file of categoryBeingPlayed as a String

    private JSONObject jsonCategoryObject;
    private final HashMap<String, Object> mapOfCategoryObjects;
    private final ArrayList<String> arrayListCorrespondingToCategoryEntityKeys;

    private final int originalKeySetSizeOfMapOfCategoryObjects;

    // Constructor
    public ADataHandler(String accessMode, String categoryBeingPlayed) throws IOException {
        this.accessMode = accessMode;
        this.categoryBeingPlayed = categoryBeingPlayed;

        switch (categoryBeingPlayed) {
            case "mobs" -> JSONFilePath = "src/Data/mobs_"+ datasetUsed + ".json";
            case "items" -> JSONFilePath = "src/Data/items" + datasetUsed +" .json";
            case "blocks" -> JSONFilePath = "src/Data/blocks_" + datasetUsed + ".json";
            default -> throw new IllegalArgumentException("invalid category selected! please check your spelling");
        }

        String content = Files.readString(Paths.get(JSONFilePath));

        // 1. Parse the string into a JSONObject
        jsonCategoryObject = new JSONObject(content);

        // 2. Convert to a standard Java Map
        mapOfCategoryObjects = (HashMap<String, Object>) jsonCategoryObject.toMap();

        originalKeySetSizeOfMapOfCategoryObjects = mapOfCategoryObjects.size();
        arrayListCorrespondingToCategoryEntityKeys = new ArrayList<>(mapOfCategoryObjects.keySet());
    }

    public String generateRandomSolution(){
        // Generates a random solution to play the game with :)
        Random r = new Random();
        int randomKeyForSolutionSelection = r.nextInt(originalKeySetSizeOfMapOfCategoryObjects);
        return arrayListCorrespondingToCategoryEntityKeys.get(randomKeyForSolutionSelection);
    }

    public String returnSetSolution(int solutionNumber) {
        // returns a solution corresponding with the given solution number (so that the simulator for the solver can use it)
        return arrayListCorrespondingToCategoryEntityKeys.get(solutionNumber);
    }

    // util functions, getter, setter etc.

    public String getAccessMode() {
        return accessMode;
    }

    public String getCategoryBeingPlayed() {
        return categoryBeingPlayed;
    }

    public String getJSONFileContentAsString() {
        return JSONFileContentAsString;
    }

    public String getJSONFilePath() {
        return JSONFilePath;
    }

    public JSONObject getJsonCategoryObject() {
        return jsonCategoryObject;
    }

    public int getOriginalKeySetSizeOfMapOfCategoryObjects() {
        return originalKeySetSizeOfMapOfCategoryObjects;
    }

    public HashMap<String, Object> getMapOfCategoryObjects() {
        return mapOfCategoryObjects;
    }

    public ArrayList<String> getArrayListCorrespondingToCategoryEntityKeys() {
        return arrayListCorrespondingToCategoryEntityKeys;
    }

    public JSONObject getSpecificJSONObject(String desiredObjectKey) {
        return jsonCategoryObject.getJSONObject(desiredObjectKey);
    }

    public static List<String> jsonArrayToList(JSONArray array) {

        List<String> list = new ArrayList<>();

        for (int i = 0; i < array.length(); i++) {
            list.add(array.getString(i));
        }

        return list;
    }

    public void setDatasetUsed(String datasetUsed) {
        this.datasetUsed = datasetUsed;
    }
}
