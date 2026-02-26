package pcy.study.aiplayground.service;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import pcy.study.aiplayground.entity.Product;
import pcy.study.aiplayground.repository.ProductRepository;

import java.util.List;

@Service
@RequiredArgsConstructor
public class ProductService {

    private final ProductRepository productRepository;

    @Transactional
    public void orderProduct(Long productId, int quantity) {
        Product product = productRepository.findById(productId)
                .orElseThrow(() -> new RuntimeException("상품을 찾을 수 없습니다."));

        product.decreaseStock(quantity);
    }

    @Transactional(readOnly = true)
    public long getTotalStockValue() {
        return productRepository.sumTotalStock();
    }
}
