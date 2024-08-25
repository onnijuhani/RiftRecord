package desktopApp;

import javafx.application.Application;
import javafx.concurrent.Task;
import javafx.scene.Scene;
import javafx.scene.control.Alert;
import javafx.scene.control.Alert.AlertType;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.control.TextField;
import javafx.scene.layout.VBox;
import javafx.stage.Stage;
import org.springframework.web.client.RestTemplate;

public class TeamProfileApp extends Application {

    @Override
    public void start(Stage primaryStage) {
        TextField teamNameField = new TextField();
        Button searchButton = new Button("Get Team Profile");
        Label profileLabel = new Label();
        TextField tagField = new TextField();
        Button addTagButton = new Button("Add Tag");

        searchButton.setOnAction(e -> {
            String teamName = teamNameField.getText();
            if (!teamName.isEmpty()) {
                Task<String> task = new Task<>() {
                    @Override
                    protected String call() {
                        RestTemplate restTemplate = new RestTemplate();
                        String pythonApiUrl = "http://localhost:5000/team/";
                        String url = pythonApiUrl + teamName;
                        return restTemplate.getForObject(url, String.class);
                    }
                };

                task.setOnSucceeded(event -> {
                    String response = task.getValue();
                    profileLabel.setText(response);
                    tagField.setDisable(false); // Enable tag field
                    addTagButton.setDisable(false); // Enable add tag button
                });

                task.setOnFailed(event -> showAlert("Error", "Failed to retrieve data."));

                new Thread(task).start();
            } else {
                showAlert("Error", "Please enter a team name.");
            }
        });

        addTagButton.setOnAction(e -> {
            String teamName = teamNameField.getText();
            String tag = tagField.getText();
            if (!teamName.isEmpty() && !tag.isEmpty()) {
                Task<Void> task = new Task<>() {
                    @Override
                    protected Void call() {
                        RestTemplate restTemplate = new RestTemplate();
                        String pythonApiUrl = "http://localhost:5000/team/";
                        String url = pythonApiUrl + teamName + "/tag";
                        restTemplate.postForObject(url, new TagRequest(tag), String.class);
                        return null;
                    }
                };

                task.setOnSucceeded(event -> showAlert("Success", "Tag added successfully."));
                task.setOnFailed(event -> showAlert("Error", "Failed to add tag."));

                new Thread(task).start();
            } else {
                showAlert("Error", "Please enter a tag.");
            }
        });

        VBox vbox = new VBox(10, teamNameField, searchButton, profileLabel, tagField, addTagButton);
        Scene scene = new Scene(vbox, 400, 300);
        primaryStage.setScene(scene);
        primaryStage.setTitle("Team Profile Viewer");
        primaryStage.show();
    }

    private void showAlert(String title, String message) {
        Alert alert = new Alert(AlertType.INFORMATION);
        alert.setTitle(title);
        alert.setHeaderText(null);
        alert.setContentText(message);
        alert.showAndWait();
    }

    public static void main(String[] args) {
        launch(args);
    }

    private record TagRequest(String tag) {
    }
}


