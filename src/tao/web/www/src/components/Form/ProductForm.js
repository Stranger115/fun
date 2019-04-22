'use strict'

import React from 'react'
import {Form, Select, InputNumber, Input, Button, message} from 'antd'
import { FormItemLayout, FormItemLayoutWithOutLabel } from "../../constants"
import axios from "axios";

const FormItem = Form.Item
const Option = Select.Option
export const EditableContext = React.createContext()



function hasErrors(fieldsError) {
  return Object.keys(fieldsError).some(field => fieldsError[field])
}


export class ProductForm extends React.Component {
  constructor(props) {
    super(props)
    this.labels = null
  }
  componentDidMount() {
    // To disabled submit button at the beginning.
    this.props.form.validateFields()
  }

  handleSubmit = async (e) => {
    e.preventDefault()
    this.props.form.validateFields(async (err, values) => {
      if (!err) {
        this.props.onSubmit()
            // edit
        await axios.post('/api/v1/product', values)
          .then(resp => {
            message.success('成功添加')
          })
          .catch(err => {
            message.error(`添加商品失败，错误：${err}`)
          })
      }
    })
  }
  handleLabel = async (e) => {
    await axios.get('/api/v1/labels')
      .then(resp => {
        this.labels = resp.data.labels
      })
      .catch(e => {
        message.error('加载分类列表失败！')
      })
  }
  render() {
    const {
      getFieldDecorator, getFieldsError, getFieldError, isFieldTouched,
    } = this.props.form
    // Only show error after a field is touched.
    const nameError = isFieldTouched('name') && getFieldError('name')
    const stockError = isFieldTouched('stock') && getFieldError('stock')
    const priceError = isFieldTouched('price') && getFieldError('price')
    const labelError = isFieldTouched('label') && getFieldError('label')
    return (
      <Form onSubmit={this.handleSubmit}>
        <Form.Item
          {...FormItemLayout}
          validateStatus={nameError ? 'error' : ''}
          help={nameError || ''}
          label='商品名'
        >
            {getFieldDecorator('name', {
            rules: [{ required: true, message: '请输入商品名!' }],
          })(
              <Input placeholder="请输入商品名" />
          )}
        </Form.Item>
        <Form.Item
          {...FormItemLayout}
          validateStatus={stockError ? 'error' : ''}
          help={stockError || ''}
          label='库存'
        >
          {getFieldDecorator('stock', {
           rules: [{ required: true, message: '请输入库存!' }],
          })(
            <InputNumber placeholder="请输入库存" />
         )}
         </Form.Item>
        <Form.Item
          {...FormItemLayout}
          validateStatus={priceError ? 'error' : ''}
          help={priceError || ''}
          label='价格'
        >
          {getFieldDecorator('price', {
            initialValue:'price',
            rules: [{ required: true, whitespace: true,  message: '请输入价格!' }],
          })(
           <InputNumber placeholder="请输入价格" />
          )}
        </Form.Item>
        <Form.Item
          {...FormItemLayout}
          validateStatus={priceError ? 'error' : ''}
          help={priceError || ''}
          label='分类'
        >
          {getFieldDecorator('label', {
            initialValue:'labell',
            rules: [{ required: true, whitespace: true,  message: '请选择分类!' }],
          })(
            <Select placeholder="请选择类型">
              {
                this.labels.map(item=>(
                  <Option key={item._id} value={item._id}>{item.name}</Option>
                ))
              }

            </Select>
          )}
        </Form.Item>
        <Form.Item {...FormItemLayoutWithOutLabel}>
          <Button
            type="primary"
            htmlType="submit"
            disabled={hasErrors(getFieldsError())}
          >
            提交
          </Button>
        </Form.Item>
      </Form>
    )
  }
}

export default Form.create()(ProductForm)


