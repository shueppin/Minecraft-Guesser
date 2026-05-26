package Game.Simulator;

import Game.Game;
import Game.GuessTemplates.GuessTemplate;
import Solver.*;
import org.json.JSONObject;

import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.util.*;
import java.util.List;

public class Simulator {
    /*
    tests current next guess computation logic against all possible games
    determines which starting guess has the lowest score over all games possible
     */


    public static class GuessScore{
        public String title;
        public double averageScore;
        private double totalScore = 0.0;
        private double totalScoresUnderConsideration = 0;

        public GuessScore(String title) {
            this.title = title;
        }
        public void addNewScoreToTotal(double newScore) {
            this.totalScore += newScore;
            totalScoresUnderConsideration++;
        }

        public void calculateAndSetAverageScore() {
            averageScore = totalScore / totalScoresUnderConsideration;
        }

    }

    private final Game game;
    public List<GuessScore> rankedGuessScores;
    private GuessScore bestScore;


    public Simulator(Game game) {
        this.game = game;
        rankedGuessScores = new ArrayList<>();
    }

    public void simulate(){

        int amountOfPossibleSolutionsToTest = game.getGameDataHandler().getOriginalKeySetSizeOfMapOfCategoryObjects();

        // iterates through each starting guess
        for(String currentFirstGuess : game.getGameDataHandler().getArrayListCorrespondingToCategoryEntityKeys()){
            System.out.println("currently evaluating: " + currentFirstGuess);

            // add new possible first guess to ranking
            rankedGuessScores.add(new GuessScore(currentFirstGuess));

            // iterate through each possible solution
            for(int currentSolutionNumber = 0; currentSolutionNumber < amountOfPossibleSolutionsToTest; currentSolutionNumber++){
                int score = 0;

                // creating new game solution
                String currentSolutionTitel = game.getGameDataHandler().returnSetSolution(currentSolutionNumber);
                JSONObject currentSolutionJSONObject = game.getGameDataHandler().getSpecificJSONObject(currentSolutionTitel);

                // setting new game solution
                game.getGameStateTracker().setSolution(currentSolutionTitel);
                game.getGameStateTracker().setSolutionJSONObject(currentSolutionJSONObject);
                game.setSolution(currentSolutionTitel);


                // simulate game for starting guess manually
                // create guess
                GuessTemplate initialGuess = game.getGameStateTracker().generateGuess(currentFirstGuess,
                        game.getGameDataHandler().getSpecificJSONObject(currentFirstGuess));

                // validate initialGuess against solution
                GuessTemplate validatedGuess = game.getGameStateTracker().validateGuess(initialGuess);

                // add first validated guess to game state
                game.getGameStateTracker().setNewGamestate(validatedGuess);

                // add first guess to total score
                score++;

                // simulate game automatically until victory
                while (!game.getGameStateTracker().solutionFound()) {
                    // calculates the next best guess
                    NextGuessComputer.SolverResult solverResult = game.getNextGuessComputer().calculateNextGuess(
                                                                  game.getGameStateTracker().getGameState(), game.getCategoryBeingPlayed());
                    String nextGuessTitel = solverResult.rankedCandidates.getFirst().title;
                    JSONObject nextGuessJSONObject = game.getGameDataHandler().getSpecificJSONObject(nextGuessTitel);

                    // generates and validates new best guess
                    GuessTemplate newGuess = game.getGameStateTracker().generateGuess(nextGuessTitel, nextGuessJSONObject);
                    GuessTemplate validatedNewGuess = game.getGameStateTracker().validateGuess(newGuess);

                    // add validated guess to game state
                    game.getGameStateTracker().setNewGamestate(validatedNewGuess);

                    // increase amount of guesses needed
                    score++;
                }

                // update average score for first guess
                rankedGuessScores.getLast().addNewScoreToTotal(score);
                // reset game state
                game.getGameStateTracker().clearGameState();
            }
            // calculate and set average score
            rankedGuessScores.getLast().calculateAndSetAverageScore();
            System.out.println("rankedGuessScores current tile: " + rankedGuessScores.getLast().title +
                    "average score is: " + rankedGuessScores.getLast().averageScore);
        }
        // rank all simulated guess average game score
        rankGuessScores();
    }


    public void createVisualisation() throws IOException {
        if (rankedGuessScores.isEmpty()) {
            System.out.println("❌ No data to visualize. Run simulate() first!");
            return;
        }

        // 1. Sort elements by performance (Ascending average score: lower is better)
        List<GuessScore> sortedScores = rankedGuessScores.stream()
                .sorted(Comparator.comparingDouble(gs -> gs.averageScore))
                .toList();

        // 2. Compute bounds for visual scaling
        double minScore = sortedScores.getFirst().averageScore;
        double maxScore = sortedScores.getLast().averageScore;
        double scoreRange = (maxScore - minScore) == 0 ? 1.0 : (maxScore - minScore);

        // 3. Layout Metrics
        int labelWidth = 250;       // Left margin room for item/mob names
        int barMaxWidth = 500;      // Maximum width of the performance metric bars
        int rightPadding = 80;      // Right margin room for exact number strings
        int rowHeight = 35;         // Vertical height allotted to each entry row
        int headerHeight = 60;      // Space for chart title and subtitle

        int totalWidth = labelWidth + barMaxWidth + rightPadding;
        int totalHeight = headerHeight + (sortedScores.size() * rowHeight) + 20;

        // 4. Initialize Graphic Context with high-fidelity anti-aliasing
        BufferedImage img = new BufferedImage(totalWidth, totalHeight, BufferedImage.TYPE_INT_ARGB);
        Graphics2D g = img.createGraphics();
        g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        g.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING, RenderingHints.VALUE_TEXT_ANTIALIAS_ON);

        // Draw Background Panel
        g.setColor(new Color(24, 25, 28)); // Sleek dark theme foundation
        g.fillRect(0, 0, totalWidth, totalHeight);

        // 5. Render Header Header Info
        g.setFont(new Font("SansSerif", Font.BOLD, 18));
        g.setColor(Color.WHITE);
        g.drawString("📊 Optimal Opening Guess Evaluation", 20, 32);

        g.setFont(new Font("SansSerif", Font.PLAIN, 12));
        g.setColor(new Color(150, 155, 165));
        g.drawString("Category: " + game.getCategoryBeingPlayed().toUpperCase() + " | Lower average turn count implies higher structural efficiency", 20, 50);

        // Draw Separation Rules Line
        g.setColor(new Color(45, 48, 54));
        g.drawLine(20, 58, totalWidth - 20, 58);

        // 6. Draw Content Row-by-Row
        int currentY = headerHeight + 25;
        for (int i = 0; i < sortedScores.size(); i++) {
            GuessScore currentEntry = sortedScores.get(i);

            // Alternate subtle backgrounds for easy scannability
            if (i % 2 == 0) {
                g.setColor(new Color(32, 34, 37));
                g.fillRect(10, currentY - 22, totalWidth - 20, rowHeight);
            }

            // Draw Ranked List Numeric Placement Identifier
            g.setFont(new Font("SansSerif", Font.BOLD, 12));
            g.setColor(i < 3 ? new Color(255, 198, 41) : new Color(110, 115, 125)); // Gold for top 3
            g.drawString(String.format("#%d", i + 1), 20, currentY);

            // Draw Item / Entity Title String
            g.setFont(new Font("SansSerif", Font.PLAIN, 13));
            g.setColor(Color.WHITE);
            String displayTitle = currentEntry.title.replace("_", " "); // Clean up snake_case labels
            g.drawString(displayTitle, 55, currentY);

            // Calculate Dynamic Performance Bar scaling bounds
            // Highly optimized choices map to full length bars, poor choices appear short
            double structuralEfficiency = (maxScore - currentEntry.averageScore) / scoreRange;
            int currentBarWidth = (int) (10 + (structuralEfficiency * (barMaxWidth - 10)));

            // Color spectrum transition calculation: Smooth Green (Best) to Red (Worst)
            float hueColorWeight = (float) (structuralEfficiency * 0.35f); // 0.35f = pure emerald green, 0.0f = pure red
            Color barFillColor = Color.getHSBColor(hueColorWeight, 0.85f, 0.85f);

            // Draw Metrics Bar Shape
            g.setColor(barFillColor);
            g.fillRoundRect(labelWidth, currentY - 14, currentBarWidth, 16, 4, 4);

            // Draw Numeric Turn Counter String Value Output
            g.setFont(new Font("Monospaced", Font.BOLD, 13));
            g.setColor(new Color(210, 215, 225));
            g.drawString(String.format("%.2f turns", currentEntry.averageScore), labelWidth + currentBarWidth + 12, currentY - 1);

            currentY += rowHeight;
        }

        // Clean up resources and output generated matrix asset to workspace root
        g.dispose();
        File outputFile = new File("solver_efficiency_map.png");
        ImageIO.write(img, "png", outputFile);
        System.out.println("🚀 Visualization map successfully exported to: " + outputFile.getAbsolutePath());
    }


    public void rankGuessScores(){
        this.bestScore = rankedGuessScores.getFirst();
        for(GuessScore guessScore : rankedGuessScores) {
            if(guessScore.averageScore < bestScore.averageScore) {
                bestScore = guessScore;
            }
        }
    }

    public List<GuessScore> getRankedGuessScores(){
        return rankedGuessScores;
    }

    public GuessScore getBestScore() {
        return bestScore;
    }
}
