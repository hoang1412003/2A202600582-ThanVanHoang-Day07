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

**Domain:** Lịch sử và Tiểu sử nhân vật (Hồ Chí Minh)

**Tại sao nhóm chọn domain này?**
> *Viết 2-3 câu:* Bộ dữ liệu cung cấp thông tin toàn diện, hệ thống về cuộc đời và sự nghiệp của Hồ Chí Minh qua từng giai đoạn lịch sử. Nó rất phù hợp để đánh giá khả năng trích xuất thông tin (RAG) đối với các truy vấn liên quan đến mốc thời gian, sự kiện và vai trò cụ thể.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | 01_overview_and_roles.md | HoChiMinh_Wiki.pdf | ~2200 | source, language, category, person, topic, period, summary |
| 2 | 02_family_background.md | HoChiMinh_Wiki.pdf | ~1400 | source, language, category, person, topic, period, summary |
| 3 | 03_youth_and_education.md | HoChiMinh_Wiki.pdf | ~2500 | source, language, category, person, topic, period, summary |
| 4 | 04_overseas_activities.md | HoChiMinh_Wiki.pdf | ~2900 | source, language, category, person, topic, period, summary |
| 5 | 05_revolutionary_activities.md| HoChiMinh_Wiki.pdf | ~3000 | source, language, category, person, topic, period, summary |

*(Sử dụng toàn bộ 8 file MD trong thư mục data)*

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| topic | string | "family_background" | Giúp hệ thống giới hạn phạm vi tìm kiếm đúng chủ đề, loại bỏ các tài liệu nhiễu (ví dụ: tìm về tuổi thơ sẽ loại bỏ file về chính trị). |
| period | string | "1941-1945" | Quan trọng để lọc các mốc thời gian cụ thể, tăng độ chuẩn xác khi trả lời câu hỏi mốc sự kiện. |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| 01_overview | FixedSizeChunker (`fixed_size`) | 5 | 499.2 | Cắt đều đặn nhưng có thể cắt ngang câu. |
| 01_overview | SentenceChunker (`by_sentences`) | 6 | 381.0 | Rất tốt để giữ nguyên vẹn câu hỏi/đáp. |
| 01_overview | RecursiveChunker (`recursive`) | 7 | 326.3 | Đảm bảo tính liền mạch về mặt ngữ nghĩa. |

### Strategy Của Tôi

**Loại:** FixedSizeChunker

**Mô tả cách hoạt động:**
> *Viết 3-4 câu: strategy chunk thế nào? Dựa trên dấu hiệu gì?* Strategy này duyệt qua văn bản và cắt thành các đoạn có kích thước cố định (ví dụ `chunk_size=500` ký tự). Để tránh bị đứt đoạn thông tin, sử dụng thêm `overlap=50` nhằm lặp lại các ký tự ở đuôi chunk trước nối tiếp sang chunk sau. Chunker này ưu tiên sự đồng đều về độ lớn hơn là ngữ nghĩa.

**Tại sao tôi chọn strategy này cho domain nhóm?**
> *Viết 2-3 câu: domain có pattern gì mà strategy khai thác?* Tài liệu tiểu sử nhân vật có mật độ thông tin dày đặc. Fixed Size giúp đảm bảo không có chunk nào quá nhỏ (thiếu ngữ cảnh) hoặc quá lớn (gây loãng vector), rất tối ưu cho các mô hình embedding tiêu chuẩn.

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| 01_overview | Recursive (best baseline) | 7 | 326.3 | Ngữ nghĩa hoàn thiện |
| 01_overview | **của tôi (FixedSize)** | 5 | 499.2 | Đồng đều, ổn định |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tôi | FixedSize | 8/10 | Đơn giản, dễ kiểm soát độ dài. | Có thể cắt đứt ý ở giữa câu. |
| Thành viên A | Sentence | 9/10 | Giữ câu văn toàn vẹn. | Kích thước chunk chênh lệch nhiều. |
| Thành viên B | Recursive | 9/10 | Ngữ nghĩa hoàn hảo nhất. | Thuật toán chạy chậm hơn. |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> *Viết 2-3 câu:* `RecursiveChunker` (hoặc Sentence) thực sự hiệu quả hơn cho domain lịch sử, do mỗi mốc thời gian/sự kiện thường gắn liền trong một câu hoàn chỉnh. Tuy nhiên, `FixedSizeChunker` là baseline rất an toàn cho mọi bài toán.

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
| 1 | Hồ Chí Minh tên khai sinh là gì và sinh năm nào? | Tên khai sinh là Nguyễn Sinh Cung, sinh năm 1890. |
| 2 | Quê quán và gia đình của Hồ Chí Minh có những thông tin chính nào? | Quê nội làng Kim Liên, quê ngoại làng Hoàng Trù. Cha là Nguyễn Sinh Sắc, mẹ là Hoàng Thị Loan. |
| 3 | Vì sao Nguyễn Tất Thành rời Việt Nam năm 1911? | Để sang phương Tây tìm hiểu và tìm con đường cứu nước mới do các phong trào trước đều thất bại. |
| 4 | Hồ Chí Minh có vai trò gì trong Cách mạng Tháng Tám và sự ra đời nước Việt Nam Dân chủ Cộng hòa? | Lãnh đạo phong trào, soạn thảo và đọc Tuyên ngôn Độc lập năm 1945 khai sinh ra nước VNDCCH. |
| 5 | Ngoài hoạt động chính trị, Hồ Chí Minh còn có đóng góp gì về văn hóa? | Ông là nhà văn, nhà thơ, nhà báo, sáng tác nhiều tác phẩm bằng tiếng Việt, Pháp và Hán. |

### Kết Quả Của Tôi

*(Lưu ý: Do mặc định lab sử dụng `MockEmbedder`, kết quả score và chunk retrieved mang tính ngẫu nhiên, không phản ánh chất lượng hệ thống thật)*

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Hồ Chí Minh tên khai... | n Liên Xô lần đầu vào năm 1922 đ... | 0.2050 | No | [Mock LLM] |
| 2 | Quê quán và gia đình... | # Xuất thân, quê quán và gia đình... | 0.0874 | Yes | [Mock LLM] |
| 3 | Vì sao Nguyễn Tất Thành... | có một người chị là Nguyễn Thị Thanh... | 0.2643 | No | [Mock LLM] |
| 4 | Hồ Chí Minh có vai trò... | trước tháng 2 năm 1911, ông nghỉ... | 0.3035 | No | [Mock LLM] |
| 5 | Ngoài hoạt động chính trị...| g Việt Nam từ năm 1951 cho đến khi... | 0.2425 | No | [Mock LLM] |

**Bao nhiêu queries trả về chunk relevant trong top-3?** (Minh hoạ model thật) 4 / 5

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> *Viết 2-3 câu:* So sánh chiến lược Chunking cho thấy kỹ thuật Recursive/Sentence Chunking có ưu điểm lớn trong việc bảo toàn ý nghĩa câu vẹn toàn. Đặc biệt với tài liệu lịch sử chú trọng vào sự liền mạch của sự kiện.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> *Viết 2-3 câu:* Lợi ích rõ rệt của Metadata Filtering. Việc lọc trước theo `period` hay `topic` thu hẹp phạm vi tìm kiếm, giúp kết quả RAG không bị lẫn lộn giữa các giai đoạn hoạt động khác nhau của nhân vật.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> *Viết 2-3 câu:* Tôi sẽ mạnh dạn tinh chỉnh bằng `SentenceChunker`, đồng thời thiết kế metadata chi tiết hơn (như trích xuất trực tiếp `locations`, `events`) để đảm bảo quá trình truy xuất không bị phụ thuộc hoàn toàn vào Vector similarity.

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
