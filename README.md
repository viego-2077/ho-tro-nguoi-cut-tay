# Word-Link Selfbot

A modular and easy-to-use Discord **selfbot** written in Python.

## Features

- 🧩 **Modular command system** — Dễ dàng thêm / xoá lệnh trong thư mục `commands/`
- 📚 **Word-chain game** — Trò chơi nối từ đơn giản và vui nhộn
- 🌍 **Translator** — Dịch văn bản giữa các ngôn ngữ
- 😂 **Fun commands** — Lệnh vui như `checkgay`, `ping`, v.v.
- ⚙️ **Multi-token support** — Chạy cùng lúc nhiều tài khoản

### Example commands included:
- **add** – Thêm cặp từ mới vào từ điển nối từ  
- **whelp** – Hiển thị danh sách từ có thể nối sau từ chỉ định  
- **thelp** – Hiển thị danh sách mã ngôn ngữ hỗ trợ dịch  
- **translate** – Dịch văn bản sang ngôn ngữ khác  
- **ping** – Kiểm tra phản hồi của bot  
- **checkgay** – Xem độ "gay" của bạn 🤣  
- **help** – Hiển thị danh sách các lệnh hiện có  

---

## Getting Started

### Prerequisites

- Python **3.8+**
- Tài khoản Discord (token user)
- Thư viện `discord.py-self` và `googletrans`

---

### Installation

1. **Clone this repository:**
    ```bash
    git clone https://github.com/viego-2077/ho-tro-nguoi-cut-tay
    cd wordlink-selfbot
    ```

2. **Cài đặt các thư viện phụ thuộc:**
    ```bash
    pip install -r requirements.txt
    ```
    > Nếu chưa có file, bạn có thể cài thủ công:
    > ```bash
    > pip install discord.py-self googletrans==4.0.0-rc1
    > ```

3. **Cấu hình bot:**

   - Mở file `config.json` và nhập thông tin:
     ```json
     {
       "prefix": "$"
     }
     ```

   - Tạo file `tokens.txt` chứa token người dùng (mỗi dòng 1 token):
     ```
     mfa.xxxxxxxxxxxxxxxxxxxxxxxxx
     mfa.yyyyyyyyyyyyyyyyyyyyyyyyy
     ```

   - Tạo file `word.txt` để làm từ điển:
     ```
     con mèo
     mèo mun
     mun đen
     ```

4. **Khởi động bot:**
    ```bash
    python main.py
    ```

---

### Folder Structure

