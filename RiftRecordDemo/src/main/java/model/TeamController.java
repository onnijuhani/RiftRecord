package model;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

@RestController
public class TeamController {

    private final String pythonApiUrl = "http://localhost:5000/team/";

    @GetMapping("/teamProfile")
    public String getTeamProfile(@RequestParam String teamName) {
        RestTemplate restTemplate = new RestTemplate();
        String response = restTemplate.getForObject(pythonApiUrl + teamName, String.class);
        return response;
    }
}
