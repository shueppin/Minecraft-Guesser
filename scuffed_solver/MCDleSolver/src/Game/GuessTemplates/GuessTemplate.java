package Game.GuessTemplates;

public class GuessTemplate {
    public String title;

    public static int compareReleaseVersions(String versionOne, String versionTwo) {
        // 1. Clean up spacing and normalize case for safe matching
        versionOne = versionOne.trim();
        versionTwo = versionTwo.trim();

        // 2. Handle Pre-Alpha Era
        if (versionOne.toLowerCase().contains("pre-alpha")) {
            if (versionTwo.toLowerCase().contains("pre-alpha")) return 0;
            return -1; // Pre-Alpha is older than anything else
        }
        if (versionTwo.toLowerCase().contains("pre-alpha")) {
            return 1; // Anything else is newer than Pre-Alpha
        }

        // 3. Handle Alpha Era
        if (versionOne.contains("Alpha")) {
            if (versionTwo.contains("Alpha")) {
                String v1Clean = versionOne.replace("Alpha", "").trim();
                String v2Clean = versionTwo.replace("Alpha", "").trim();
                return compareSubVersions(v1Clean, v2Clean);
            }
            return -1; // Alpha is older than Beta or Official Release
        }
        if (versionTwo.contains("Alpha")) {
            return 1; // Beta or Official Release is newer than Alpha
        }

        // 4. Handle Beta Era
        if (versionOne.contains("Beta")) {
            if (versionTwo.contains("Beta")) {
                String v1Clean = versionOne.replace("Beta", "").trim();
                String v2Clean = versionTwo.replace("Beta", "").trim();
                return compareSubVersions(v1Clean, v2Clean);
            }
            return -1; // Beta is older than Official Release
        }
        if (versionTwo.contains("Beta")) {
            return 1; // Official Release is newer than Beta
        }

        // 5. Handle Official Releases (No prefix strings)
        return compareSubVersions(versionOne, versionTwo);
    }

    // Safe helper method to compare numeric tokens (e.g., "1.4.2" vs "1.8")
    private static int compareSubVersions(String v1, String v2) {
        String[] levels1 = v1.split("\\.");
        String[] levels2 = v2.split("\\.");

        int maxLength = Math.max(levels1.length, levels2.length);

        for (int i = 0; i < maxLength; i++) {
            int num1 = i < levels1.length ? Integer.parseInt(levels1[i].replaceAll("[^0-9]", "")) : 0;
            int num2 = i < levels2.length ? Integer.parseInt(levels2[i].replaceAll("[^0-9]", "")) : 0;

            if (num1 < num2) return -1;
            if (num1 > num2) return 1;
        }
        return 0;
    }
}


/*
    All versions with letters
    pre-alpha
    Alpha 1.0.1
    Alpha 1.0.4
    Alpha 1.0.6
    Alpha 1.1.11
    Alpha 1.1.14
    Alpha 1.0.17
    Alpha 1.2
    Beta 1.2
    Beta 1.3
    Beta 1.5
    Beta 1.6
    Beta 1.7
    Beta 1.8
     */
