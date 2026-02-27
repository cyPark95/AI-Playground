package pcy.study.aiplayground.exception;

import lombok.Getter;

@Getter
public class AiPlaygroundException extends RuntimeException {
    private final ErrorCode errorCode;

    public AiPlaygroundException(ErrorCode errorCode) {
        super(errorCode.getMessage());
        this.errorCode = errorCode;
    }
}
