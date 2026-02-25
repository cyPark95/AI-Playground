package pcy.study.aiplayground.service;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.annotation.Transactional;
import pcy.study.aiplayground.entity.Product;
import pcy.study.aiplayground.repository.ProductRepository;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

@SpringBootTest
@Transactional
class ProductServiceTest {

    @Autowired
    private ProductService productService;

    @Autowired
    private ProductRepository productRepository;

    private Long savedProductId;

    @BeforeEach
    void setUp() {
        Product product = new Product("테스트 상품", 100);
        Product savedProduct = productRepository.save(product);
        savedProductId = savedProduct.getId();
    }

    @Test
    @DisplayName("상품 주문 시 재고가 정상적으로 감소해야 한다.")
    void orderProduct_Success() {
        // given
        int orderQuantity = 10;

        // when
        productService.orderProduct(savedProductId, orderQuantity);

        // then
        Product product = productRepository.findById(savedProductId).orElseThrow();
        assertThat(product.getStock()).isEqualTo(90);
    }

    @Test
    @DisplayName("재고보다 많은 수량을 주문하면 예외가 발생해야 한다.")
    void orderProduct_Fail_LackOfStock() {
        // given
        int orderQuantity = 101;

        // when & then
        assertThatThrownBy(() -> productService.orderProduct(savedProductId, orderQuantity))
                .isInstanceOf(RuntimeException.class)
                .hasMessage("재고가 부족합니다.");
    }

    @Test
    @DisplayName("전체 상품의 재고 합계를 정확히 계산해야 한다.")
    void getTotalStockValue_Success() {
        // given
        productRepository.save(new Product("상품2", 50));
        productRepository.save(new Product("상품3", 30));

        // when
        long totalStock = productService.getTotalStockValue();

        // then
        // 기존 100 (setUp) + 50 + 30 = 180
        assertThat(totalStock).isEqualTo(180);
    }
}
