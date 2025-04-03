package org.alfresco.service;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Service;

@Service
public class ChatService {

    private final ChatClient ollamaClient;
    private final ChatClient modelRunnerClient;

    public ChatService(@Qualifier("ollamaChatClient") ChatClient ollamaClient,
                       @Qualifier("openaiChatClient") ChatClient modelRunnerClient) {
        this.ollamaClient = ollamaClient;
        this.modelRunnerClient = modelRunnerClient;
    }

    public String askOllama(String question) {
        return ollamaClient.prompt(question).call().chatResponse().getResult().getOutput().getText();
    }

    public String askModelRunner(String question) {
        return modelRunnerClient.prompt(question).call().chatResponse().getResult().getOutput().getText();
    }
}
