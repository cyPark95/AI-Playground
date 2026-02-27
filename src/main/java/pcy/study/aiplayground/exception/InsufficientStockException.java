package pcy.study.aiplayground.exception;

public class InsufficientStockException extends AiPlaygroundException {
    public InsufficientStockException() {
        super(ErrorCode.INSUFFICIENT_STOCK);
    }
}
