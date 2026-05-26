package Game;

import javax.swing.*;
import java.awt.*;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

import Game.GuessTemplates.*;

public class Visualizer {

    private JFrame frame;
    private JTextArea displayArea;
    private JTextField inputField;
    private JButton guessButton;

    private BlockingQueue<String> inputQueue;

    public Visualizer() {
        inputQueue = new LinkedBlockingQueue<>();

        frame = new JFrame("Minecraft Guesser Game (Ambiguous)");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(650, 600); // Expanded slightly vertically for live metrics
        frame.setLayout(new BorderLayout());

        displayArea = new JTextArea();
        displayArea.setEditable(false);
        displayArea.setFont(new Font("Monospaced", Font.PLAIN, 13));
        displayArea.setMargin(new Insets(10, 10, 10, 10));
        JScrollPane scrollPane = new JScrollPane(displayArea);
        frame.add(scrollPane, BorderLayout.CENTER);

        JPanel bottomPanel = new JPanel(new BorderLayout());
        inputField = new JTextField();
        guessButton = new JButton("Guess!");

        bottomPanel.add(inputField, BorderLayout.CENTER);
        bottomPanel.add(guessButton, BorderLayout.EAST);
        frame.add(bottomPanel, BorderLayout.SOUTH);

        inputField.addActionListener(e -> submitGuess());
        guessButton.addActionListener(e -> submitGuess());

        frame.setLocationRelativeTo(null);
        frame.setVisible(true);

        displayMessage("Welcome to MCdle! Start typing your guesses below.\n");
    }

    private void submitGuess() {
        String text = inputField.getText().trim().toLowerCase();
        if (!text.isEmpty()) {
            inputQueue.add(text);
            inputField.setText("");
        }
    }

    public String getUserInput() {
        try {
            return inputQueue.take();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return null;
        }
    }

    public void displayMessage(String message) {
        displayArea.append(message + "\n");
        displayArea.setCaretPosition(displayArea.getDocument().getLength());
    }

    // Displays structural guess metrics matching internal engine logic
    public void displayGuessResult(String guessName, GuessTemplate guess) {
        StringBuilder sb = new StringBuilder();
        sb.append("===============================================================\n");
        sb.append(" GUESS: ").append(guessName.toUpperCase()).append("\n");
        sb.append("---------------------------------------------------------------\n");
        sb.append(String.format(" %-18s | %-22s | %-15s\n", "PROPERTY", "YOUR VALUE", "RESULT"));
        sb.append("---------------------------------------------------------------\n");

        if (guess instanceof MobsGuessTemplate mob) {
            sb.append(formatLine("Title", mob.title, formatBinary(mob.titleCorrectness)));
            sb.append(formatLine("Initial Release", mob.initial_release, formatRange(mob.releaseCorrectness)));
            sb.append(formatLine("Health", String.valueOf(mob.health), formatRange(mob.healthCorrectness)));
            sb.append(formatLine("Height", String.valueOf(mob.height), formatRange(mob.heightCorrectness)));
            sb.append(formatLine("Behavior", mob.behaviour.toString(), formatPartial(mob.behaviourCorrectness)));
            sb.append(formatLine("Spawn Biome/Type", mob.spawn.toString(), formatPartial(mob.spawnCorrectness)));
            sb.append(formatLine("Classification", mob.classification.toString(), formatPartial(mob.classificationCorrectness)));

        } else if (guess instanceof ItemsGuessTemplate item) {
            sb.append(formatLine("Title", item.title, formatBinary(item.titleCorrectness)));
            sb.append(formatLine("Initial Release", item.initial_release, formatRange(item.releaseCorrectness)));
            sb.append(formatLine("Stackable Amount", String.valueOf(item.stackable), formatRange(item.stackSizeCorrectness)));
            sb.append(formatLine("Rarity Tier", item.rarity, formatRange(item.rarityCorrectness)));
            sb.append(formatLine("Creative Tabs", item.inventory_categories.toString(), formatPartial(item.creativeInventoryCategoryCorrectness)));
            sb.append(formatLine("Renewable", item.renewable, formatPartial(item.renewableCorrectness)));
            sb.append(formatLine("Recipe Station", item.recipe.toString(), formatPartial(item.recipeCorrectness)));
            sb.append(formatLine("Loot Source", item.loot.toString(), formatPartial(item.lootCorrectness)));

        } else if (guess instanceof BlocksGuessTemplate block) {
            sb.append(formatLine("Title", block.title, formatBinary(block.titleCorrectness)));
            sb.append(formatLine("Initial Release", block.initial_release, formatRange(block.releaseCorrectness)));
            sb.append(formatLine("Stackable Amount", String.valueOf(block.stackable), formatRange(block.stackSizeCorrectness)));
            sb.append(formatLine("Mining Tool", block.tool.toString(), formatPartial(block.toolsCorrectness)));
            sb.append(formatLine("Blast Resistance", String.valueOf(block.blast_resistance), formatRange(block.blastResistanceCorrectness)));
            sb.append(formatLine("Hardness", String.valueOf(block.hardness), formatRange(block.hardnessCorrectness)));
            sb.append(formatLine("Flammable", block.flammable, formatPartial(block.flammableCorrectness)));
            sb.append(formatLine("Is Full Block", block.full_block, formatPartial(block.fullBlockCorrectness)));
        }

        sb.append("===============================================================\n");
        displayArea.append(sb.toString());
        displayArea.setCaretPosition(displayArea.getDocument().getLength());
    }

    /**
     * Renders a live leaderboard chart of calculated choices inside the visualizer console.
     */
    public void displaySolverAnalysis(java.util.List<Solver.NextGuessComputer.CandidateEntropy> rankedCandidates, int remainingCandidates) {
        StringBuilder sb = new StringBuilder();
        sb.append("💡 [SHANNON ENTROPY LIVE RANKINGS]\n");
        sb.append(String.format(" 🧩 Remaining hidden suspect entries: %d\n", remainingCandidates));
        sb.append("---------------------------------------------------------------\n");
        sb.append(String.format("  %-5s | %-25s | %-15s\n", "RANK", "MOB GUESS OPTION", "EXPECTED INFO"));
        sb.append("---------------------------------------------------------------\n");

        if (rankedCandidates.isEmpty()) {
            sb.append("  No matching entries left in the active pool.\n");
        } else {
            // Display up to the top 10 choices to maintain readability
            int displayLimit = Math.min(rankedCandidates.size(), 10);
            for (int i = 0; i < displayLimit; i++) {
                Solver.NextGuessComputer.CandidateEntropy candidate = rankedCandidates.get(i);
                sb.append(String.format("  #%-4d | %-25s | %.4f bits\n",
                        (i + 1),
                        candidate.title.toUpperCase(),
                        candidate.entropy));
            }

            if (rankedCandidates.size() > 10) {
                sb.append("---------------------------------------------------------------\n");
                sb.append(String.format("  ... and %d more options evaluated in background.\n",
                        rankedCandidates.size() - 10));
            }
        }
        sb.append("===============================================================\n\n");

        displayArea.append(sb.toString());
        displayArea.setCaretPosition(displayArea.getDocument().getLength());
    }


    private String formatLine(String property, String value, String outcome) {
        if (value.length() > 22) {
            value = value.substring(0, 19) + "...";
        }
        return String.format(" %-18s | %-22s | %-15s\n", property, value, outcome);
    }

    private String formatRange(int code) {
        return switch (code) {
            case 0 -> "Too Low  ↓";
            case 1 -> "Too High ↑";
            case 2 -> "Correct  ✓";
            default -> "Unknown";
        };
    }

    private String formatPartial(int code) {
        return switch (code) {
            case 0 -> "Incorrect ✗";
            case 1 -> "Partial   ◒";
            case 2 -> "Correct   ✓";
            default -> "Unknown";
        };
    }

    private String formatBinary(int code) {
        return switch (code) {
            case 0 -> "Incorrect ✗";
            case 1 -> "Correct   ✓";
            default -> "Unknown";
        };
    }

    public void displayVictory(String solution, int totalGuesses) {
        StringBuilder sb = new StringBuilder();
        sb.append("\n🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉\n");
        sb.append("   VICTORY! You found the solution: ").append(solution.toUpperCase()).append("\n");
        sb.append("   Total attempts required: ").append(totalGuesses).append("\n");
        sb.append("🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉\n\n");

        displayArea.append(sb.toString());
        displayArea.setCaretPosition(displayArea.getDocument().getLength());

        JOptionPane.showMessageDialog(frame,
                "Correct! The answer was " + solution + ".\nYou won in " + totalGuesses + " guesses!",
                "GG WP!",
                JOptionPane.INFORMATION_MESSAGE);
    }
}