package pcy.study.aiplayground.exception;

public class ProductNotFoundException extends AiPlaygroundException {
    public ProductNotFoundException() {
        super(ErrorCode.PRODUCT_NOT_FOUND);
    }
}
