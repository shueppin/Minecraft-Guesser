package Game.GuessTemplates;

import org.json.JSONObject;

import static Data.ADataHandler.jsonArrayToList;

import java.util.List;

public class MobsGuessTemplate extends GuessTemplate{
    public String initial_release; // range
    public double health; // range
    public double height; // range
    public List<String> behaviour; // partial
    public List<String> spawn; // partial
    public List<String> classification; // partial

    // correctness State
    // Range
    // 0 = lower, 1 = higher, 2 = correct

    // Binary
    // 0 = false, 1 = correct

    //Partials
    // 0 = false, 1 = partial, 2 = correct
    public int titleCorrectness;
    public int releaseCorrectness;
    public int healthCorrectness;
    public int heightCorrectness;
    public int behaviourCorrectness;
    public int spawnCorrectness;
    public int classificationCorrectness;


    public MobsGuessTemplate(String title, String release, double health, double height,
                             List<String> behaviour, List<String> spawn, List<String> classification) {
        this.title = title;
        this.initial_release = release;
        this.health = health;
        this.height = height;
        this.behaviour = behaviour;
        this.spawn = spawn;
        this.classification = classification;
    }

    public MobsGuessTemplate() {
    }

    public static MobsGuessTemplate validateMobGuess(MobsGuessTemplate mobGuessToValidate, JSONObject solutionJSONObject){
        // Binary: 0 = false, 1 = correct
        if(mobGuessToValidate.title.equals(solutionJSONObject.getString("title"))) {
            mobGuessToValidate.titleCorrectness = 1;
        } else {
            mobGuessToValidate.titleCorrectness = 0;
        }

        // Range: 0 = lower, 1 = higher, 2 = correct
        int releaseComparison = compareReleaseVersions(mobGuessToValidate.initial_release, solutionJSONObject.getString("initial_release"));
        if(releaseComparison < 0) {
            mobGuessToValidate.releaseCorrectness = 0; // mobGuessToValidate has lower release version than solution
        } else if (releaseComparison > 0) {
            mobGuessToValidate.releaseCorrectness = 1; // mobGuessToValidate has higher release version than solution
        }
        else mobGuessToValidate.releaseCorrectness = 2; // correct release

        double targetHealth = solutionJSONObject.getDouble("health");
        if(mobGuessToValidate.health == targetHealth) {
            mobGuessToValidate.healthCorrectness = 2;
        } else if (mobGuessToValidate.health < targetHealth) {
            mobGuessToValidate.healthCorrectness = 0; // Guess is lower than target
        } else {
            mobGuessToValidate.healthCorrectness = 1; // Guess is higher than target
        }

        double targetHeight = solutionJSONObject.getDouble("height");
        if(mobGuessToValidate.height == targetHeight) {
            mobGuessToValidate.heightCorrectness = 2;
        } else if (mobGuessToValidate.height < targetHeight) {
            mobGuessToValidate.heightCorrectness = 0; // Guess is lower than target
        } else {
            mobGuessToValidate.heightCorrectness = 1; // Guess is higher than target
        }

        // Partials: 0 = false, 1 = partial, 2 = correct
        List<String> targetBehaviour = jsonArrayToList(solutionJSONObject.getJSONArray("behavior"));
        if (mobGuessToValidate.behaviour.equals(targetBehaviour)) {
            mobGuessToValidate.behaviourCorrectness = 2;
        } else if (mobGuessToValidate.behaviour.stream().anyMatch(targetBehaviour::contains)) {
            mobGuessToValidate.behaviourCorrectness = 1;
        } else {
            mobGuessToValidate.behaviourCorrectness = 0;
        }

        List<String> targetSpawn = jsonArrayToList(solutionJSONObject.getJSONArray("spawn"));
        if (mobGuessToValidate.spawn.equals(targetSpawn)) {
            mobGuessToValidate.spawnCorrectness = 2;
        } else if (mobGuessToValidate.spawn.stream().anyMatch(targetSpawn::contains)) {
            mobGuessToValidate.spawnCorrectness = 1;
        } else {
            mobGuessToValidate.spawnCorrectness = 0;
        }

        List<String> targetClassification = jsonArrayToList(solutionJSONObject.getJSONArray("classification"));
        if (mobGuessToValidate.classification.equals(targetClassification)) {
            mobGuessToValidate.classificationCorrectness = 2;
        } else if (mobGuessToValidate.classification.stream().anyMatch(targetClassification::contains)) {
            mobGuessToValidate.classificationCorrectness = 1;
        } else {
            mobGuessToValidate.classificationCorrectness = 0;
        }

        return mobGuessToValidate;
    }
    public String getTitle(){
        return title;
    }
        /*
        Docs so i dont go crazy:
        behaviour:
        0 = passive
        1 = neutral
        2 = hostile

        spawn:
        0 = biom
        1 = light level
        2 = breeding
        3 = structure
        4 = block
        5 = spawner
        6 = Grass,
        7 = Jockey,
        8 = Projectile,
        9 = Conversion
        10 = Summon
        11 = Reinforcements
        12 = raids
        13 = Overworld
        14 = Duplication
        15 = Magic
        16 = Lightning
        17 = Hatching
        18 = Sieges

        classification:
        0 = animal
        1 = monster
        2 = undead
        3 = aquatic
        4 = Arthropods
        5 = Illager
        6 = Boss mobs
        7 = none
         */


}
