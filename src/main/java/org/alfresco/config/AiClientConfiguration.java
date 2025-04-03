package org.alfresco.config;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class AiClientConfiguration {

    @Bean(name = "openaiChatClient")
    public ChatClient openaiChatClient(@Qualifier("openAiChatModel") ChatModel openAiModel) {
        return ChatClient.create(openAiModel);
    }

    @Bean(name = "ollamaChatClient")
    public ChatClient ollamaChatClient(@Qualifier("ollamaChatModel") ChatModel ollamaModel) {
        return ChatClient.create(ollamaModel);
    }

}
