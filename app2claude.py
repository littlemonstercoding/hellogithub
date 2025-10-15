from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# เก็บข้อมูลในหน่วยความจำ (ใช้งานจริงควรใช้ฐานข้อมูล)
tools = []
next_id = 1

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ระบบบันทึกเครื่องมือช่าง</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #667eea;
            margin-bottom: 30px;
            text-align: center;
            font-size: 2em;
        }
        .form-section {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #333;
            font-weight: 600;
        }
        input[type="text"], input[type="number"], textarea {
            width: 100%;
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        input:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        textarea {
            resize: vertical;
            min-height: 80px;
        }
        button {
            background: #667eea;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: background 0.3s;
        }
        button:hover {
            background: #5568d3;
        }
        .btn-success {
            background: #28a745;
        }
        .btn-success:hover {
            background: #218838;
        }
        .btn-danger {
            background: #dc3545;
            padding: 8px 15px;
            font-size: 14px;
        }
        .btn-danger:hover {
            background: #c82333;
        }
        .btn-warning {
            background: #ffc107;
            padding: 8px 15px;
            font-size: 14px;
            margin-right: 5px;
        }
        .btn-warning:hover {
            background: #e0a800;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background: #667eea;
            color: white;
            font-weight: 600;
        }
        tr:hover {
            background: #f8f9fa;
        }
        .actions {
            white-space: nowrap;
        }
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #999;
        }
        .total {
            text-align: right;
            margin-top: 20px;
            font-size: 18px;
            font-weight: bold;
            color: #667eea;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 ระบบบันทึกเครื่องมือช่าง</h1>
        
        <div class="form-section">
            <h2 style="margin-bottom: 20px; color: #333;">
                {% if edit_mode %}แก้ไขข้อมูล{% else %}เพิ่มเครื่องมือใหม่{% endif %}
            </h2>
            <form method="POST" action="{% if edit_mode %}/update/{{ tool.id }}{% else %}/add{% endif %}">
                <div class="form-group">
                    <label>รหัสสินค้า:</label>
                    <input type="text" name="code" value="{{ tool.code if edit_mode else '' }}" required>
                </div>
                <div class="form-group">
                    <label>ชื่อสินค้า:</label>
                    <input type="text" name="name" value="{{ tool.name if edit_mode else '' }}" required>
                </div>
                <div class="form-group">
                    <label>รายละเอียด:</label>
                    <textarea name="description">{{ tool.description if edit_mode else '' }}</textarea>
                </div>
                <div class="form-group">
                    <label>ราคา (บาท):</label>
                    <input type="number" name="price" step="0.01" value="{{ tool.price if edit_mode else '' }}" required>
                </div>
                <div class="form-group">
                    <label>จำนวน:</label>
                    <input type="number" name="quantity" value="{{ tool.quantity if edit_mode else '' }}" required>
                </div>
                <button type="submit" class="{% if edit_mode %}btn-warning{% else %}btn-success{% endif %}">
                    {% if edit_mode %}บันทึกการแก้ไข{% else %}เพิ่มข้อมูล{% endif %}
                </button>
                {% if edit_mode %}
                    <a href="/"><button type="button">ยกเลิก</button></a>
                {% endif %}
            </form>
        </div>

        <h2 style="margin-bottom: 15px; color: #333;">รายการเครื่องมือ</h2>
        {% if tools %}
            <table>
                <thead>
                    <tr>
                        <th>รหัสสินค้า</th>
                        <th>ชื่อสินค้า</th>
                        <th>รายละเอียด</th>
                        <th>ราคา</th>
                        <th>จำนวน</th>
                        <th>จัดการ</th>
                    </tr>
                </thead>
                <tbody>
                    {% for tool in tools %}
                    <tr>
                        <td>{{ tool.code }}</td>
                        <td>{{ tool.name }}</td>
                        <td>{{ tool.description }}</td>
                        <td>{{ "%.2f"|format(tool.price) }} บาท</td>
                        <td>{{ tool.quantity }}</td>
                        <td class="actions">
                            <a href="/edit/{{ tool.id }}"><button class="btn-warning">แก้ไข</button></a>
                            <form method="POST" action="/delete/{{ tool.id }}" style="display: inline;">
                                <button type="submit" class="btn-danger" onclick="return confirm('ต้องการลบรายการนี้?')">ลบ</button>
                            </form>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            <div class="total">
                จำนวนรายการทั้งหมด: {{ tools|length }} รายการ
            </div>
        {% else %}
            <div class="empty-state">
                <p>ยังไม่มีข้อมูลเครื่องมือ</p>
                <p>เริ่มต้นเพิ่มข้อมูลด้านบน</p>
            </div>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, tools=tools, edit_mode=False)

@app.route('/add', methods=['POST'])
def add_tool():
    global next_id
    tool = {
        'id': next_id,
        'code': request.form['code'],
        'name': request.form['name'],
        'description': request.form['description'],
        'price': float(request.form['price']),
        'quantity': int(request.form['quantity'])
    }
    tools.append(tool)
    next_id += 1
    return redirect(url_for('index'))

@app.route('/edit/<int:tool_id>')
def edit_tool(tool_id):
    tool = next((t for t in tools if t['id'] == tool_id), None)
    if tool:
        return render_template_string(HTML_TEMPLATE, tools=tools, edit_mode=True, tool=tool)
    return redirect(url_for('index'))

@app.route('/update/<int:tool_id>', methods=['POST'])
def update_tool(tool_id):
    tool = next((t for t in tools if t['id'] == tool_id), None)
    if tool:
        tool['code'] = request.form['code']
        tool['name'] = request.form['name']
        tool['description'] = request.form['description']
        tool['price'] = float(request.form['price'])
        tool['quantity'] = int(request.form['quantity'])
    return redirect(url_for('index'))

@app.route('/delete/<int:tool_id>', methods=['POST'])
def delete_tool(tool_id):
    global tools
    tools = [t for t in tools if t['id'] != tool_id]
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)