import Data.ADataHandler;
import Game.*;
import Solver.NextGuessComputer;
import netscape.javascript.JSObject;

import java.util.Arrays;
import java.util.Map;
import java.io.IOException;

public class DevTestClass {
    public static void main(String[] args) throws IOException {

        //ADataHandler testHandler = new ADataHandler("random", "items");

        //System.out.println(testHandler.getMapOfCategoryObjects().keySet().toString());
        //System.out.println(testHandler.generateRandomSolution());

        Game game = new Game("random", "mobs");
    }
}
