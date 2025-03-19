<template>
  <el-collapse-transition>
    <div class="analysis-results" v-loading="loading" v-if="visible">
      <div v-if="!loading && !data" class="no-data">
        <el-empty description="暂无分析数据" />
      </div>

      <div v-if="data" class="results-container">
        <div class="close-button">
          <el-button type="text" :icon="Close" circle @click="handleClose" />
        </div>
        <div class="results-header">
          <h3>
            分析结果
            <el-tag size="small" effect="plain" class="task-id">
              {{ taskId }}
            </el-tag>
          </h3>
          <div class="summary-info">
            <el-tag type="info"
              >总商品: {{ data.summary.total_products }}</el-tag
            >
            <el-tag type="success"
              >已处理: {{ data.summary.processed_count }}</el-tag
            >
            <el-tag type="primary"
              >方案一: {{ data.summary.scheme1_count }}</el-tag
            >
            <el-tag type="warning"
              >方案二: {{ data.summary.scheme2_count }}</el-tag
            >
          </div>
        </div>

        <el-tabs v-model="activeTab" class="results-tabs">
          <template #default>
            <el-scrollbar max-height="80vh">
              <el-tab-pane label="方案一结果" name="scheme1">
                <div class="product-list">
                  <div
                    v-for="product in data.products.filter(
                      (p) => p.matches_1.length > 0
                    )"
                    :key="product.product_id"
                    class="product-card"
                  >
                    <div class="product-info">
                      <div class="product-image">
                        <el-image
                          :src="product.cover_url"
                          fit="cover"
                          :preview-src-list="[product.cover_url]"
                          :preview-teleported="true"
                          :initial-index="0"
                          :zoom-rate="1.2"
                        >
                          <template #error>
                            <div class="image-error">
                              <el-icon><Picture /></el-icon>
                            </div>
                          </template>
                        </el-image>
                      </div>
                      <div class="product-details">
                        <h4>{{ product.product_name }}</h4>
                        <div class="product-meta">
                          <span>类别: {{ product.category }}</span>
                          <span>价格: {{ product.avg_price }}</span>
                          <span>销量: {{ product.total_sale_nd_cnt }}</span>
                          <span>达人数: {{ product.influencers_count }}</span>
                          <span>评分: {{ product.product_rating }}</span>
                        </div>
                      </div>
                    </div>

                    <div class="matches-container">
                      <div class="matches-header">
                        <h5>匹配商品 ({{ product.matches_1.length }})</h5>
                      </div>
                      <div class="matches-scroll-container">
                        <el-button
                          class="scroll-button prev"
                          :icon="ArrowLeft"
                          circle
                          @click="scrollMatches(product.product_id, 'prev')"
                        />
                        <div
                          class="matches-list"
                          :ref="
                            (el) => setMatchesListRef(product.product_id, el)
                          "
                        >
                          <div
                            v-for="(match, index) in product.matches_1"
                            :key="index"
                            class="match-item"
                          >
                            <div class="match-image">
                              <el-image
                                :src="match.image_url"
                                fit="cover"
                                :preview-src-list="
                                  getMatchesImageList(product.matches_1)
                                "
                                :preview-teleported="true"
                                :initial-index="index"
                                :zoom-rate="1.2"
                              >
                                <template #error>
                                  <div class="image-error">
                                    <el-icon><Picture /></el-icon>
                                  </div>
                                </template>
                              </el-image>
                            </div>
                            <div class="match-details">
                              <h5 :title="match.title">
                                {{ match.title || "未知商品" }}
                              </h5>
                              <p>价格: {{ match.price || "未知" }}</p>
                              <el-link
                                type="primary"
                                :href="match.product_url"
                                target="_blank"
                              >
                                查看商品
                              </el-link>
                            </div>
                          </div>
                        </div>
                        <el-button
                          class="scroll-button next"
                          :icon="ArrowRight"
                          circle
                          @click="scrollMatches(product.product_id, 'next')"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </el-tab-pane>

              <el-tab-pane label="方案二结果" name="scheme2">
                <div class="product-list">
                  <div
                    v-for="product in data.products.filter(
                      (p) => p.matches_2.length >= 2
                    )"
                    :key="product.product_id"
                    class="product-card"
                  >
                    <div class="product-info">
                      <div class="product-image">
                        <el-image
                          :src="product.cover_url"
                          fit="cover"
                          :preview-src-list="[product.cover_url]"
                          :preview-teleported="true"
                          :initial-index="0"
                          :zoom-rate="1.2"
                        >
                          <template #error>
                            <div class="image-error">
                              <el-icon><Picture /></el-icon>
                            </div>
                          </template>
                        </el-image>
                      </div>
                      <div class="product-details">
                        <h4>{{ product.product_name }}</h4>
                        <div class="product-meta">
                          <span>类别: {{ product.category }}</span>
                          <span>价格: {{ product.avg_price }}</span>
                          <span>销量: {{ product.total_sale_nd_cnt }}</span>
                          <span>达人数: {{ product.influencers_count }}</span>
                          <span>评分: {{ product.product_rating }}</span>
                        </div>
                      </div>
                    </div>

                    <div class="matches-container">
                      <div class="matches-header">
                        <h5>高相似度商品 ({{ product.matches_2.length }})</h5>
                      </div>
                      <div class="matches-scroll-container">
                        <el-button
                          class="scroll-button prev"
                          :icon="ArrowLeft"
                          circle
                          @click="
                            scrollMatches(
                              product.product_id + '_scheme2',
                              'prev'
                            )
                          "
                        />
                        <div
                          class="matches-list"
                          :ref="
                            (el) =>
                              setMatchesListRef(
                                product.product_id + '_scheme2',
                                el
                              )
                          "
                        >
                          <div
                            v-for="(match, index) in product.matches_2.sort(
                              (a, b) => b.similarity - a.similarity
                            )"
                            :key="index"
                            class="match-item"
                          >
                            <div class="match-image">
                              <el-image
                                :src="match.image_url"
                                fit="cover"
                                :preview-src-list="
                                  getMatchesImageList(product.matches_2)
                                "
                                :preview-teleported="true"
                                :initial-index="index"
                                :zoom-rate="1.2"
                              >
                                <template #error>
                                  <div class="image-error">
                                    <el-icon><Picture /></el-icon>
                                  </div>
                                </template>
                              </el-image>
                            </div>
                            <div class="match-details">
                              <h5 :title="match.title">
                                {{ match.title || "未知商品" }}
                              </h5>
                              <p>价格: {{ match.price || "未知" }}</p>
                              <p class="similarity">
                                相似度:
                                <el-progress
                                  :percentage="
                                    Math.round(match.similarity * 100)
                                  "
                                  :color="getSimilarityColor(match.similarity)"
                                />
                              </p>
                              <el-link
                                type="primary"
                                :href="match.product_url"
                                target="_blank"
                              >
                                查看商品
                              </el-link>
                            </div>
                          </div>
                        </div>
                        <el-button
                          class="scroll-button next"
                          :icon="ArrowRight"
                          circle
                          @click="
                            scrollMatches(
                              product.product_id + '_scheme2',
                              'next'
                            )
                          "
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </el-tab-pane>
            </el-scrollbar>
          </template>
        </el-tabs>
      </div>
    </div>
  </el-collapse-transition>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import { Picture, Close, ArrowLeft, ArrowRight } from "@element-plus/icons-vue";
import { getAnalysisResults } from "../api";
import { ElMessage } from "element-plus";

const props = defineProps({
  taskId: String,
  visible: Boolean,
});

const emit = defineEmits(["close"]);

const loading = ref(false);
const data = ref(null);
const activeTab = ref("scheme1");
const matchesListRefs = ref({});
const scrollPositions = ref({});

const handleClose = () => {
  emit("close");
};

const setMatchesListRef = (productId, el) => {
  if (el) matchesListRefs.value[productId] = el;
};

const scrollMatches = (productId, direction) => {
  const container = matchesListRefs.value[productId];
  if (!container) return;

  const scrollAmount = container.clientWidth * 0.8; // 滚动80%的容器宽度
  const targetScroll =
    direction === "prev"
      ? container.scrollLeft - scrollAmount
      : container.scrollLeft + scrollAmount;

  container.scrollTo({
    left: targetScroll,
    behavior: "smooth",
  });
};

const canScrollPrev = (productId) => {
  const container = matchesListRefs.value[productId];
  return container && container.scrollLeft > 0;
};

const canScrollNext = (productId) => {
  const container = matchesListRefs.value[productId];
  if (!container) return false;
  return container.scrollLeft < container.scrollWidth - container.clientWidth;
};

const getMatchesImageList = (matches) => {
  return matches.map((match) => match.image_url);
};

const getSimilarityColor = (similarity) => {
  if (similarity >= 0.9) return "#67C23A";
  if (similarity >= 0.8) return "#E6A23C";
  return "#F56C6C";
};

const fetchAnalysisData = async () => {
  try {
    loading.value = true;
    const response = await getAnalysisResults(props.taskId);
    data.value = response;
    if (!response || !response.products || !response.summary) {
      throw new Error("分析数据格式不正确");
    }

    scrollPositions.value = {};
    response.products.forEach((product) => {
      scrollPositions.value[product.product_id] = { scrollLeft: 0 };
    });
  } catch (error) {
    console.error("获取分析结果失败:", error);
    ElMessage.error(error.response?.data?.detail || "获取分析结果失败");
    data.value = null;
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  if (props.visible) {
    fetchAnalysisData();
  }
});

// 监听visible变化
watch(
  () => props.visible,
  (newVal) => {
    if (newVal) {
      fetchAnalysisData();
    }
  }
);

// 监听taskId变化
watch(
  () => props.taskId,
  async (newVal, oldVal) => {
    if (newVal && newVal !== oldVal) {
      data.value = null; // 清空旧数据
      await fetchAnalysisData();
    }
  }
);
</script>

<style lang="less" scoped>
.analysis-results {
  margin-top: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  padding: 20px;
  min-height: 300px;
  position: relative;

  .close-button {
    position: absolute;
    top: 16px;
    right: 16px;
    z-index: 1;
  }

  .no-data {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 200px;
  }

  .results-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    h3 {
      margin: 0;
      font-size: 18px;
      color: #303133;
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .summary-info {
      display: flex;
      gap: 10px;

      .el-tag {
        padding: 0 10px;
        height: 28px;
        line-height: 28px;
      }
    }
  }

  .results-tabs {
    .product-list {
      display: flex;
      flex-direction: column;
      gap: 20px;

      .product-card {
        border: 1px solid #ebeef5;
        border-radius: 8px;
        padding: 15px;
        transition: all 0.3s ease;

        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .product-info {
          display: flex;
          gap: 15px;
          margin-bottom: 15px;

          .product-image {
            width: 80px;
            height: 80px;
            flex-shrink: 0;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

            .el-image {
              width: 100%;
              height: 100%;
              border-radius: 4px;
              overflow: hidden;
              transition: transform 0.3s ease;

              &:hover {
                transform: scale(1.05);
              }
            }

            .image-error {
              width: 100%;
              height: 100%;
              display: flex;
              justify-content: center;
              align-items: center;
              background-color: #f5f7fa;
              color: #909399;
            }
          }

          .product-details {
            flex: 1;

            h4 {
              margin: 0 0 10px 0;
              font-size: 15px;
              color: #303133;
              white-space: nowrap;
              overflow: hidden;
              text-overflow: ellipsis;
            }

            .product-meta {
              display: flex;
              flex-wrap: wrap;
              gap: 10px;

              span {
                font-size: 13px;
                color: #606266;
                background-color: #f5f7fa;
                padding: 2px 8px;
                border-radius: 4px;
              }
            }
          }
        }

        .matches-container {
          .matches-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;

            h5 {
              margin: 0;
              font-size: 15px;
              color: #606266;
            }
          }

          .matches-scroll-container {
            position: relative;
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 0 20px;
            min-height: 240px;

            .scroll-button {
              position: absolute;
              z-index: 1;
              --el-button-size: 32px;
              --el-button-bg-color: #fff;
              --el-button-text-color: var(--el-color-primary);
              --el-button-hover-bg-color: #fff;
              --el-button-hover-text-color: var(--el-color-primary-light-3);
              box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
              transition: all 0.3s ease;
              opacity: 0.9;

              &.prev {
                left: -16px;
                &:hover {
                  transform: translateX(-2px);
                }
              }

              &.next {
                right: -16px;
                &:hover {
                  transform: translateX(2px);
                }
              }

              &:hover {
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
                opacity: 1;
              }
            }
          }

          .matches-list {
            display: flex;
            gap: 15px;
            overflow-x: auto;
            scroll-behavior: smooth;
            scrollbar-width: none;
            -ms-overflow-style: none;
            padding: 8px 4px;
            width: 100%;
            position: relative;
            z-index: 0;

            &::-webkit-scrollbar {
              display: none;
            }

            .match-item {
              flex: 0 0 240px;
              border: 1px solid #ebeef5;
              border-radius: 6px;
              padding: 10px;
              transition: all 0.3s ease;

              .match-image {
                width: 100%;
                height: 160px;
                margin-bottom: 10px;
                border-radius: 6px;
                overflow: hidden;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
              }

              .match-details {
                h5 {
                  margin: 0 0 5px 0;
                  font-size: 14px;
                  color: #303133;
                  display: -webkit-box;
                  -webkit-line-clamp: 2;
                  -webkit-box-orient: vertical;
                  overflow: hidden;
                  text-overflow: ellipsis;
                  height: 40px;
                  max-width: 100%;
                }

                p {
                  margin: 0 0 5px 0;
                  font-size: 13px;
                  color: #606266;
                }

                .similarity {
                  margin-bottom: 10px;

                  .el-progress {
                    margin-top: 5px;
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}

:deep(.el-image-viewer__wrapper) {
  .el-image-viewer__btn {
    opacity: 0.7;
    &:hover {
      opacity: 1;
    }
  }

  .el-image-viewer__actions {
    opacity: 0.9;
    padding: 10px 20px;
  }

  .el-image-viewer__canvas {
    display: flex;
    justify-content: center;
    align-items: center;

    img {
      max-width: 90vw;
      max-height: 90vh;
      object-fit: contain;
    }
  }
}
</style>
