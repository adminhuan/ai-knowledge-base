import { API_BASE_URL } from '@/config'

// 通用文件上传（头像等）
export function uploadFile(filePath, folder = 'avatar') {
	return new Promise((resolve, reject) => {
		const token = uni.getStorageSync('token')
		
		uni.uploadFile({
			url: API_BASE_URL + '/api/upload/file-to-cos',
			filePath: filePath,
			name: 'file',
			formData: { folder },
			header: {
				'Authorization': `Bearer ${token}`
			},
			success: (res) => {
				try {
					const data = JSON.parse(res.data)
					if (data.code === 0) {
						resolve(data)
					} else {
						reject(new Error(data.message || '上传失败'))
					}
				} catch (e) {
					reject(new Error('响应解析失败'))
				}
			},
			fail: (err) => {
				reject(err)
			}
		})
	})
}

// H5 端使用 fetch + FormData 上传
async function uploadWithFetch(url, file, prompt) {
	const token = uni.getStorageSync('token')
	const formData = new FormData()
	formData.append('file', file)
	formData.append('prompt', prompt)
	
	const response = await fetch(url, {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${token}`
		},
		body: formData
	})
	
	const data = await response.json()
	if (data.code === 0) {
		return data
	} else {
		throw new Error(data.message || data.detail || '解析失败')
	}
}

export function parseImage(filePathOrFile, prompt = '请描述这张图片的内容') {
	return new Promise((resolve, reject) => {
		const token = uni.getStorageSync('token')
		
		// #ifdef H5
		// H5 端：如果传入的是 File 对象，用 fetch
		if (filePathOrFile instanceof File || filePathOrFile instanceof Blob) {
			uploadWithFetch(API_BASE_URL + '/api/upload/image', filePathOrFile, prompt)
				.then(resolve)
				.catch(reject)
			return
		}
		// #endif
		
		uni.uploadFile({
			url: API_BASE_URL + '/api/upload/image',
			filePath: filePathOrFile,
			name: 'file',
			formData: {
				prompt: prompt
			},
			header: {
				'Authorization': `Bearer ${token}`
			},
			success: (res) => {
				try {
					const data = JSON.parse(res.data)
					if (data.code === 0) {
						resolve(data)
					} else {
						reject(new Error(data.message || '图片解析失败'))
					}
				} catch (e) {
					reject(new Error('响应解析失败'))
				}
			},
			fail: (err) => {
				reject(err)
			}
		})
	})
}

// 上传文件到腾讯云 COS
export function uploadFileToCOS(fileData, filename, fileType, description = '') {
	return new Promise((resolve, reject) => {
		const token = uni.getStorageSync('token')
		
		uni.request({
			url: API_BASE_URL + '/api/upload/to-cos',
			method: 'POST',
			header: {
				'Authorization': `Bearer ${token}`,
				'Content-Type': 'application/json'
			},
			data: {
				file_data: fileData,
				filename: filename,
				file_type: fileType,
				description: description
			},
			success: (res) => {
				if (res.data.code === 0) {
					resolve(res.data)
				} else {
					reject(new Error(res.data.message || '上传失败'))
				}
			},
			fail: (err) => {
				reject(err)
			}
		})
	})
}

export function parseFile(filePathOrFile, prompt = '请描述这个文件的内容') {
	return new Promise((resolve, reject) => {
		const token = uni.getStorageSync('token')
		
		// #ifdef H5
		// H5 端：如果传入的是 File 对象，用 fetch
		if (filePathOrFile instanceof File || filePathOrFile instanceof Blob) {
			uploadWithFetch(API_BASE_URL + '/api/upload/file', filePathOrFile, prompt)
				.then(resolve)
				.catch(reject)
			return
		}
		// #endif
		
		uni.uploadFile({
			url: API_BASE_URL + '/api/upload/file',
			filePath: filePathOrFile,
			name: 'file',
			formData: {
				prompt: prompt
			},
			header: {
				'Authorization': `Bearer ${token}`
			},
			success: (res) => {
				try {
					const data = JSON.parse(res.data)
					if (data.code === 0) {
						resolve(data)
					} else {
						reject(new Error(data.message || '文件解析失败'))
					}
				} catch (e) {
					reject(new Error('响应解析失败'))
				}
			},
			fail: (err) => {
				reject(err)
			}
		})
	})
}
