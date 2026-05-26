import Game.*;

import java.io.IOException;

public class Main {
    public static void main(String[] args) throws IOException {

        String[] accessModes = {"random", "testing", "simulating", "manualVerification"};
        String[] categories = {"mobs", "items", "blocks"};

        int accessModeChoice= 1;
        int categoryChoice = 2;

        Game game = new Game(accessModes[accessModeChoice], categories[categoryChoice]);
    }
}