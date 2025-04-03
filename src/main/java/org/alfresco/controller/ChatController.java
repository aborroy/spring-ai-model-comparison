package org.alfresco.controller;

import org.alfresco.service.ChatService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/chat")
public class ChatController {

    private final ChatService chatService;

    public ChatController(ChatService chatService) {
        this.chatService = chatService;
    }

    @PostMapping("/ollama")
    public ResponseEntity<String> chatWithOllama(@RequestBody Map<String, String> body) {
        String response = chatService.askOllama(body.get("message"));
        return ResponseEntity.ok(response);
    }

    @PostMapping("/runner")
    public ResponseEntity<String> chatWithModelRunner(@RequestBody Map<String, String> body) {
        String response = chatService.askModelRunner(body.get("message"));
        return ResponseEntity.ok(response);
    }
}
