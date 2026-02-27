package pcy.study.aiplayground;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.annotation.EnableCaching;

@SpringBootApplication
@EnableCaching
public class AiPlaygroundApplication {

    public static void main(String[] args) {
        SpringApplication.run(AiPlaygroundApplication.class, args);
    }

}
