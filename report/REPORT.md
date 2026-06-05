# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** [Tên sinh viên]
**Nhóm:** [Tên nhóm]
**Ngày:** [Ngày nộp]

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> *Viết 1-2 câu:* Cosine similarity cao có nghĩa là hai vector đại diện hướng về cùng một phía trong không gian vector, thể hiện hai đoạn văn bản có sự tương đồng mạnh về ý nghĩa, ngữ cảnh hoặc chủ đề bất kể độ dài.

**Ví dụ HIGH similarity:**
- Sentence A: Con mèo đang ngủ trên ghế sofa.
- Sentence B: Một chú mèo con đang nằm nghỉ trên chiếc ghế dài.
- Tại sao tương đồng: Cả hai cùng mô tả một chủ thể và hành động mang ý nghĩa tương đương (mèo ngủ/nghỉ trên ghế).

**Ví dụ LOW similarity:**
- Sentence A: Con mèo đang ngủ trên ghế sofa.
- Sentence B: Thị trường chứng khoán giảm mạnh do lãi suất tăng.
- Tại sao khác: Hai câu thuộc hai chủ đề hoàn toàn khác nhau (động vật vs tài chính).

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> *Viết 1-2 câu:* Euclidean distance bị ảnh hưởng lớn bởi độ dài của vector (độ dài văn bản), trong khi cosine similarity chỉ quan tâm đến góc giữa hai vector, giúp so sánh sự tương đồng về nghĩa tốt hơn mà không bị sai lệch bởi độ dài câu.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11)
> *Đáp án:* 23 chunks

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> *Viết 1-2 câu:* Chunk count sẽ tăng lên thành 25 chunks. Overlap lớn hơn giúp duy trì tính liền mạch của ngữ cảnh, hạn chế việc chia cắt các câu hoặc ý tưởng ở phần ranh giới giữa các chunk.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** [ví dụ: Customer support FAQ, Vietnamese law, cooking recipes, ...]

**Tại sao nhóm chọn domain này?**
> *Viết 2-3 câu:*

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| | | | |
| | | | |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| | FixedSizeChunker (`fixed_size`) | | | |
| | SentenceChunker (`by_sentences`) | | | |
| | RecursiveChunker (`recursive`) | | | |

### Strategy Của Tôi

**Loại:** [FixedSizeChunker / SentenceChunker / RecursiveChunker / custom strategy]

**Mô tả cách hoạt động:**
> *Viết 3-4 câu: strategy chunk thế nào? Dựa trên dấu hiệu gì?*

**Tại sao tôi chọn strategy này cho domain nhóm?**
> *Viết 2-3 câu: domain có pattern gì mà strategy khai thác?*

**Code snippet (nếu custom):**
```python
# Paste implementation here
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| | best baseline | | | |
| | **của tôi** | | | |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tôi | | | | |
| [Tên] | | | | |
| [Tên] | | | | |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> *Viết 2-3 câu:*

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> *Viết 2-3 câu:* Dùng `re.split(r'(\. |\! |\? |\.\n)', text)` để tách text theo ranh giới câu mà vẫn giữ được dấu câu. Sau đó ghép lại và gom nhóm các câu vào chunk cho đến khi đủ `max_sentences_per_chunk`, kết hợp dùng hàm `strip()` để dọn khoảng trắng thừa.

**`RecursiveChunker.chunk` / `_split`** — approach:
> *Viết 2-3 câu:* Hàm đệ quy `_split` chia văn bản bằng separator đầu tiên trong danh sách. Base case là đoạn văn nhỏ hơn `chunk_size` (trả về luôn) hoặc không còn separator nào (ép chia cứng theo kích thước); nếu đoạn văn chia ra vẫn lớn thì gọi lại đệ quy với danh sách separator tiếp theo.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> *Viết 2-3 câu:* Hàm `add_documents` sinh vector cho tài liệu và nạp đồng thời vào in-memory list (dạng dict) và ChromaDB (nếu có). `search` dùng in-memory sẽ tính dot product (cosine similarity) giữa query embedding và tất cả docs, rồi sắp xếp theo `score` giảm dần để lấy `top_k`.

**`search_with_filter` + `delete_document`** — approach:
> *Viết 2-3 câu:* `search_with_filter` thực hiện pre-filtering để chọn ra các chunk thoả mãn điều kiện metadata trước rồi mới truyền vào tính điểm `_search_records`. `delete_document` cập nhật lại in-memory list bằng list comprehension lọc bỏ record nào có `id` hay metadata `doc_id` trùng khớp.

### KnowledgeBaseAgent

**`answer`** — approach:
> *Viết 2-3 câu:* Gọi `store.search` để lấy list các đoạn text liên quan, sau đó nối các văn bản vào `context_str`. Cuối cùng inject nó cùng với `question` vào trong prompt rồi gửi đến `llm_fn` để tạo câu trả lời.

### Test Results

```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.3, pluggy-1.6.0 -- C:\Users\MSIo\AppData\Local\Programs\Python\Python314\python.exe
cachedir: .pytest_cache
rootdir: D:\vin-ai-thuc-chien\2A202600582-ThanVanHoang-Day07
plugins: anyio-4.13.0, langsmith-0.8.8
collecting ... collected 42 items
...
============================= 42 passed in 0.11s ==============================
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | I love programming in Python. | Coding in Python is my passion. | high | N/A | N/A |
| 2 | The cat sat on the mat. | A dog barked loudly at the mailman. | low | N/A | N/A |
| 3 | Artificial intelligence is the future. | Machine learning shapes tomorrow. | high | N/A | N/A |
| 4 | I want to eat pizza tonight. | The weather is very nice today. | low | N/A | N/A |
| 5 | Water boils at 100 degrees Celsius. | H2O becomes gas at 100C. | high | N/A | N/A |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> *Viết 2-3 câu:* (Lưu ý: Lab dùng MockEmbedder nên score thực tế sẽ random không ý nghĩa, bảng này dùng để dự đoán nếu là model thật). Điều quan trọng nhất rút ra là embedding model chất lượng sẽ nhận ra sự liên hệ về mặt ngữ nghĩa (ví dụ "Water" và "H2O") mà không cần đối chiếu từng ký tự, cho phép retrieval cực kỳ chính xác.

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. **5 queries phải trùng với các thành viên cùng nhóm.**

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Bao nhiêu queries trả về chunk relevant trong top-3?** __ / 5

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> *Viết 2-3 câu:*

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> *Viết 2-3 câu:*

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | / 5 |
| Document selection | Nhóm | / 10 |
| Chunking strategy | Nhóm | / 15 |
| My approach | Cá nhân | / 10 |
| Similarity predictions | Cá nhân | / 5 |
| Results | Cá nhân | / 10 |
| Core implementation (tests) | Cá nhân | / 30 |
| Demo | Nhóm | / 5 |
| **Tổng** | | **/ 100** |
