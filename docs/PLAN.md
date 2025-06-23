Tuyệt vời\! Đây là một hướng đi rất rõ ràng và khả thi. Việc sử dụng `serena` làm một "Code Intelligence Server" chuyên dụng và xây dựng hệ thống Multi-Agent xung quanh nó bằng ADK và A2A là một kiến trúc rất mạnh mẽ và linh hoạt.

Dưới đây là kế hoạch chi tiết để triển khai dự án của bạn, tuân thủ tất cả các yêu cầu và lưu ý đã nêu.

### **Kế hoạch Triển khai Hệ thống Multi-Agent Review Code**

-----

### **Giai đoạn 0: Thiết lập Nền tảng và Môi trường**

Mục tiêu của giai đoạn này là chuẩn bị một môi trường phát triển hoàn chỉnh, sẵn sàng cho việc xây dựng các agent.

1.  **Cấu trúc Thư mục Dự án:**
    Tạo một cấu trúc thư mục rõ ràng để quản lý các agent và các thành phần chung.

    ```bash
    code-review-mas/
    ├── agents/                  # Nơi chứa mã nguồn của từng agent
    │   ├── local_code_agent/
    │   ├── git_retrieval_agent/
    │   ├── static_analysis_agent/
    │   ├── ... (các agent khác)
    │   └── orchestrator_agent/
    ├── scripts/                 # Các script để khởi chạy agent, serena, etc.
    │   ├── run_serena_server.sh
    │   ├── run_local_code_agent.sh
    │   └── ...
    ├── pyproject.toml           # Quản lý project và dependencies bằng uv
    └── .env                     # Lưu trữ các biến môi trường (API keys, etc.)
    ```

2.  **Thiết lập Môi trường với `uv`:**

      * Cài đặt `uv`: `pip install uv` (nếu chưa có).
      * Tạo môi trường ảo: `uv venv`
      * Kích hoạt môi trường: `source .venv/bin/activate`

3.  **Cài đặt Thư viện Cốt lõi:**
    Sử dụng `uv` để cài đặt các gói cần thiết vào môi trường ảo. Thêm các thư viện này vào `pyproject.toml`.

    ```bash
    # Cài đặt các gói chính
    uv pip install "google-adk==1.4.2" "a2a-sdk==0.2.8"

    # Cài đặt các thư viện cho serena (dựa trên pyproject.toml của serena)
    # Giả định bạn đã clone serena vào một thư mục khác
    uv pip install -e path/to/serena

    # Các thư viện phụ trợ khác
    uv pip install python-dotenv
    ```

4.  **Chạy `serena` như một MCP Server Độc lập:**

      * **Mục tiêu:** Khởi chạy `serena` để nó lắng nghe các kết nối MCP từ các agent khác.
      * **Thực thi:**
          * Tạo một file script `scripts/run_serena_server.sh`.
          * Nội dung file này sẽ điều hướng đến thư mục `serena` và chạy `mcp_server.py` của nó. Quan trọng là phải truyền vào `--project-path` một cách linh động hoặc sử dụng một thư mục tạm thời chung. Vì hệ thống dành cho nhiều người dùng, `project_path` sẽ được cung cấp bởi các agent sau này. Ta có thể khởi tạo `serena` với một thư mục gốc (workspace) nơi nó sẽ tạo các thư mục con cho mỗi phiên làm việc.
          * Ví dụ: `python scripts/mcp_server.py --host 0.0.0.0 --port 50051 --project-path /tmp/serena_workspace`. Các agent sau này sẽ tương tác với các project cụ thể bên trong workspace này.

-----

### **Giai đoạn 1: Phát triển các Agent "Thu thập Mã nguồn"**

Mục tiêu là tạo ra các agent có khả năng cung cấp mã nguồn cho các agent phân tích.

1.  **Agent 1: `LocalCodeAgent`**

      * **Vai trò:** Nhận một đường dẫn thư mục trên máy local và cung cấp đường dẫn đó cho các agent khác. Đây là agent đơn giản nhất để bắt đầu và kiểm tra giao tiếp A2A.
      * **Triển khai:**
          * Tạo thư mục `agents/local_code_agent/`.
          * **A2A Server:** Sử dụng `a2a-sdk` để tạo một server lắng nghe.
          * **Agent Card:** Định nghĩa `local_code_agent.card.json` với một `skill` tên là `provide_code_path` có input là `path: str`.
          * **Logic:** Handler của skill sẽ kiểm tra xem đường dẫn có tồn tại không. Nếu có, nó sẽ trả về đường dẫn tuyệt đối. Nếu không, trả về lỗi. Agent này **không cần** tương tác với `serena`.

2.  **Agent 2: `GitRetrievalAgent`**

      * **Vai trò:** Nhận URL của một kho Git, clone hoặc pull về một thư mục tạm thời và cung cấp đường dẫn của thư mục đó.
      * **Triển khai:**
          * Tạo thư mục `agents/git_retrieval_agent/`.
          * **A2A Server:** Tương tự `LocalCodeAgent`.
          * **Agent Card:** Định nghĩa skill `clone_repository` với các input như `repo_url: str`, `branch: str (optional)`.
          * **Logic:**
              * Sử dụng thư viện `gitpython` (cài bằng `uv pip install gitpython`).
              * Handler sẽ tạo một thư mục tạm thời duy nhất (ví dụ trong `/tmp/code_reviews/<session_id>`).
              * Thực hiện `git.Repo.clone_from(...)`.
              * Trả về đường dẫn đến thư mục đã clone.

-----

### **Giai đoạn 2: Phát triển các Agent "Phân tích" sử dụng `serena`**

Đây là giai đoạn cốt lõi, nơi sức mạnh của `serena` được tận dụng.

1.  **Agent 3: `StaticAnalysisAgent` (SA Agent)**

      * **Vai trò:** Nhận đường dẫn mã nguồn, sử dụng các công cụ SAST (ví dụ: Semgrep) thông qua `serena` và trả về kết quả.
      * **Triển khai:**
          * Tạo thư mục `agents/static_analysis_agent/`.
          * **A2A Server:** Định nghĩa skill `run_sast_scan` với input `code_path: str`.
          * **ADK & MCP Client:**
              * Sử dụng `LlmAgent` từ `google-adk`. Mặc dù agent này chủ yếu gọi tool, việc dùng `LlmAgent` giúp nó có khả năng diễn giải kết quả hoặc quyết định chạy tool nào trong tương lai.
              * Viết một hàm để kết nối đến `serena` MCP Server (địa chỉ `host:port` lấy từ file `.env`).
              * Sử dụng `adk.mcp.McpTool` để định nghĩa một công cụ gọi đến `serena`. Tham khảo tài liệu ADK về MCP Tools.
          * **Logic:**
            1.  Nhận `code_path` qua A2A.
            2.  **Quan trọng:** Trước khi chạy scan, agent cần yêu cầu `serena` "nhận biết" project này. Điều này có thể được thực hiện bằng một tool của `serena` như `set_project_root_path(path)`.
            3.  Agent sẽ gọi MCP tool `execute_shell_command` của `serena` để chạy: `semgrep scan --json .` bên trong `code_path`.
            4.  Nhận kết quả JSON từ `serena`, có thể thực hiện một số xử lý sơ bộ (ví dụ: tóm tắt số lượng lỗi).
            5.  Trả kết quả về qua A2A.

2.  **Agent 4: `PRImpactAnalysisAgent` (PRIA)**

      * **Vai trò:** Phân tích tác động của thay đổi, tìm các vùng bị ảnh hưởng. Đây là nơi `serena` phát huy giá trị lớn nhất.
      * **Triển khai:**
          * Tạo thư mục `agents/pr_impact_analysis_agent/`.
          * **A2A Server:** Định nghĩa skill `analyze_impact` với input là `code_path: str`, `changed_file: str`, `changed_function: str`.
          * **ADK & MCP Client:** Tương tự SA Agent.
          * **Logic:**
            1.  Nhận thông tin về thay đổi.
            2.  Yêu cầu `serena` set project root.
            3.  Sử dụng MCP tool của `serena` là `find_referencing_symbols` để tìm tất cả các nơi `changed_function` được gọi.
            4.  Tổng hợp danh sách các file và hàm bị ảnh hưởng.
            5.  Trả về danh sách này qua A2A.

-----

### **Giai đoạn 3: Phát triển Agent Điều phối và Hoàn thiện Luồng**

1.  **Agent 5: `OrchestratorAgent` (OA)**
      * **Vai trò:** "Bộ não" của hệ thống. Nhận yêu cầu từ người dùng, gọi các agent chuyên biệt theo đúng thứ tự, tổng hợp kết quả và trả về cho người dùng.
      * **Triển khai:**
          * Tạo thư mục `agents/orchestrator_agent/`.
          * **ADK & A2A Client:**
              * Agent này sẽ là một `LlmAgent` để có thể hiểu ngôn ngữ tự nhiên từ người dùng.
              * Nó sẽ là một A2A Client, sử dụng `a2a-sdk` để kết nối và gọi các `skill` của các agent khác (SA, PRIA, ...).
              * Nó sẽ không chạy A2A Server (trừ khi bạn muốn các agent khác gọi lại nó).
          * **Logic (Ví dụ luồng review local folder):**
            1.  `OA` nhận yêu cầu: "Review thư mục `/path/to/my/project`".
            2.  `OA` phân tích yêu cầu, xác định cần `LocalCodeAgent`. Nó gửi A2A request đến `LocalCodeAgent` với skill `provide_code_path` và payload là `/path/to/my/project`.
            3.  `LocalCodeAgent` trả về đường dẫn đã được xác thực.
            4.  `OA` nhận đường dẫn, sau đó gửi A2A request đến `StaticAnalysisAgent` với skill `run_sast_scan` và payload là đường dẫn đó.
            5.  `StaticAnalysisAgent` chạy phân tích qua `serena` và trả về kết quả.
            6.  `OA` nhận kết quả SAST, định dạng lại và trình bày cho người dùng.

-----

### **Giai đoạn 4: Mở rộng và Hoàn thiện**

  * **Phát triển các Agent còn lại:** Lặp lại quy trình ở Giai đoạn 2 cho `SCAA_Agent`, `DiagramGenerationAgent`, `CodeSuggestionAgent`, `QAA_Agent` theo thiết kế trong `DESIGN.md`.
  * **Giao diện người dùng:** Xây dựng một giao diện dòng lệnh (CLI) hoặc một Web UI đơn giản để người dùng có thể tương tác với `OrchestratorAgent`.
  * **Quản lý phiên (Session Management):** Vì hệ thống cho nhiều người dùng, `OrchestratorAgent` cần quản lý các phiên làm việc riêng biệt. Mỗi yêu cầu mới có thể tạo ra một session ID, được sử dụng để tạo các thư mục tạm thời riêng biệt, tránh xung đột.
  * **Đóng gói và Triển khai:** Sử dụng Docker để đóng gói từng agent (hoặc cả hệ thống) để dễ dàng triển khai. `serena` đã có sẵn Dockerfile, bạn có thể tham khảo.

Kế hoạch này chia dự án thành các phần nhỏ, dễ quản lý và cho phép bạn thấy được giá trị ở mỗi bước. Bằng cách bắt đầu với các agent đơn giản và sau đó tích hợp dần với `serena`, bạn có thể đảm bảo nền tảng hoạt động ổn định trước khi đi vào các logic phức tạp. Chúc bạn thành công\!