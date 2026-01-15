// 假设 axios 已经通过 <script> 标签引入，这里直接使用全局变量 axios
function getRequest(url, params, callback) {
    let headers = {};
    if (params && params.token) {
        //headers.Authorization = `Bearer ${params.token}`;
        headers.Authorization = `Bearer ${params.token}`;
        // 从 params 中移除 token，避免作为查询参数
        delete params.token;
    }
    axios.get(url, {
        headers: headers,
        params: params
    })
      .then(response => {
            callback(response.data,'success');
        })
      .catch(error => {
            callback(error, 'error');
        });
}

function postRequest(url, data, callback) {
    // 默认不指定时也为'application/json'
    const contentType = 'application/json';
    let headers = {
        'Content-Type': contentType
        // 'Content-Type': 'application/x-www-form-urlencoded'
        // 'Content-Type': 'multipart/form-data'
        // 'Content-Type': 'text/plain'
    };
    if (data && data.token) {
        headers.Authorization = `Bearer ${data.token}`;
        // 从 data 中移除 token，避免作为请求体数据
        delete data.token;
    }
    let processedData = data;
    if (contentType === 'application/x-www-form-urlencoded') {
        processedData = new URLSearchParams();
        for (const [key, value] of Object.entries(data)) {
            processedData.append(key, value);
        }
    }

    axios.post(url, processedData, {
        headers: headers
    })
      .then(response => {
            callback(response.data,'success');
        })
      .catch(error => {
            callback(error, "error");
        });
}
    
function postRequestFile(url, data, callback) {
    // 默认不指定时也为'application/json'
    let headers = {
        'Content-Type': 'multipart/form-data'
    };
    if (data && data.token) {
        headers.Authorization = `Bearer ${data.token}`;
        // 从 data 中移除 token，避免作为请求体数据
        delete data.token;
    }
    let processedData = new FormData();
    for (const [key, value] of Object.entries(data)) {
        if (value instanceof FileList) {
            for (let i = 0; i < value.length; i++) {
                processedData.append(key, value[i]);
            }
        } else {
            processedData.append(key, value);
        }
    }
    // 当使用 FormData 时，不需要手动设置 Content-Type，浏览器会自动添加带边界的 Content-Type
    delete headers['Content-Type'];

    axios.post(url, processedData, {
        headers: headers
    })
      .then(response => {
            callback(response.data,'success');
        })
      .catch(error => {
            callback(error, "error");
        });
}

// 文件上传使用示例
function uploadFiles() {
    const fileInput = document.getElementById('fileInput');
    const files = fileInput.files;
    const postUrl = 'https://example.com/api/upload';
    const postData = {
        token: 'xxx',
        files: files
    };
    postRequestFile(postUrl, postData, (error, result) => {
        if (error) {
            console.error('文件上传出错:', error);
        } else {
            console.log('文件上传成功:', result);
        }
    });
}
function formatTime(orderTime) {
    // 替换空格为 T
    const isoDateTime = orderTime.replace(' ', 'T');
    const now = new Date();
    const orderDateTime = new Date(isoDateTime);
    
    // 检查日期是否有效
    if (isNaN(orderDateTime.getTime())) {
        return "无效日期";
    }
    
    const timeDiff = now - orderDateTime; // 时间差（毫秒）
    const minutesDiff = Math.floor(timeDiff / (1000 * 60)); // 时间差（分钟）

    if (minutesDiff < 0) {
        return ""; // 处理未来时间
    } else if(minutesDiff <= 0){
        return "刚刚";
    }
    else if (minutesDiff < 10) {
        return `${minutesDiff}分钟前`; // 0-9分钟
    } else if (minutesDiff < 60) {
        // 10-59分钟，按10分钟分段
        const roundedMinutes = Math.floor(minutesDiff / 10) * 10;
        return `${roundedMinutes}分钟前`;
    } else {
        // ≥60分钟，按小时或天计算
        const hoursDiff = Math.floor(minutesDiff / 60);
        if (hoursDiff < 24) {
            return `${hoursDiff}小时前`; // 24小时内
        } else {
            const daysDiff = Math.floor(hoursDiff / 24);
            return `${daysDiff}天前`; // 超过24小时
        }
    }
}

function formatDistance(distance) {
    if (distance < 1000) {
        return `${distance}米`;
    } else {
        const km = distance / 1000;
        return `${km.toFixed(1)}公里`;
    }
}

function formatDuration(duration){
    if(duration<60)
        return `${duration}秒`
    else if(duration<3600)
        return `${Math.floor(duration/60)}分钟`
    else
        return `${Math.floor(duration/3600)}小时`
}
function formatPhone(p){
    const phone = p;
    if (!phone) return '';
    return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2');
}
function transformRegionData(data) {
    // 创建一个映射表，用于快速查找每个区域
    const regionMap = new Map();

    // 第一步：处理所有区域数据，构建映射表
    data.forEach(item => {
        // 提取城市名称的第一个汉字（如果是直辖市，去除"市"字）
        const shortName = item.name
        
        // 构建当前区域的节点
        const node = {
            value: item.name,
            id: item.id,
            label: shortName,
            children: []
        };

        regionMap.set(item.id, node);
    });

    // 第二步：构建树形结构
    const rootRegions = [];

    data.forEach(item => {
        const node = regionMap.get(item.id);

        if (item.parent_id === 0) {
            // 如果是一级区域，直接添加到根节点数组
            rootRegions.push(node);
        } else {
            // 否则，找到其父节点并添加到父节点的 children 数组中
            const parentNode = regionMap.get(item.parent_id);
            if (parentNode) {
                parentNode.children.push(node);
            }
        }
    });

    console.log(rootRegions)

    return rootRegions;
}
// 获取区域数据
function get_region_list(call_back) {
    $.ajax({
        url: '/admin/region',
        type: 'get',
        dataType: 'json',
        success: (res) => {
            if (res.status != 0){
                call_back(null,null)
                return
            }

            var parents = []
            for (let i in res.data) {
                var data = {}
                if (res.data[i].parent_id == 0) {
                    data['value'] = res.data[i].name
                    data['label'] = res.data[i].name
                    data['id'] = res.data[i].id

                    let id = res.data[i].id
                    var children = []
                    for (let j in res.data) {
                        if (res.data[j].parent_id == id) {
                            children.push({ 'value': res.data[j].name, label: res.data[j].name,'id': id })
                        }
                    }

                    data['children'] = children

                    parents.push(data)
                }
            }

            //that.regionOptions = parents
            if(call_back)
                call_back(parents,res.data)
        }
    })
}

function getQueryParams() {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const params = {};
    for (const [key, value] of urlParams.entries()) {
        params[key] = value;
    }
    return params;
}

function get_expirt_time(created_at,day){
    // 假设 created_at 是一个字符串，格式为 'YYYY-MM-DD'
    let createdAtString = created_at;// '2023-10-01'; // 示例日期
    let daysToAdd = day; // 要添加的天数

    // 解析 created_at 为 Date 对象
    let createdAt = new Date(createdAtString);

    // 添加指定天数
    createdAt.setDate(createdAt.getDate() + daysToAdd);

    // 获取当前日期
    let currentDate = new Date();

    // 比较两个日期
    if (createdAt > currentDate) {
      // 计算相差天数
      let timeDifference = createdAt - currentDate;
      let dayDifference = timeDifference / (1000 * 3600 * 24);
      console.log(`大于当前日期，相差 ${Math.ceil(dayDifference)} 天`);
      return [0,`${Math.ceil(dayDifference)}天后过期`]
    } else {
      console.log('小于或等于当前日期');
      return [-1,'已过期']
    }
  }

  // 时间格式化函数
    function formatTimepy(gmtTime) {
        const date = new Date(gmtTime);
        
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0'); // 月份从0开始
        const day = String(date.getDate()).padStart(2, '0');
        
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        const seconds = String(date.getSeconds()).padStart(2, '0');

        return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    }