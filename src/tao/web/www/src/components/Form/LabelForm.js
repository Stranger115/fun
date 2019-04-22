'use strict'

import React from 'react'
import {Form, Input, Button, message} from 'antd'
import { FormItemLayout, FormItemLayoutWithOutLabel } from "../../constants"
import axios from "axios";


function hasErrors(fieldsError) {
  return Object.keys(fieldsError).some(field => fieldsError[field])
}


export class LabelForm extends React.Component {
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
    this.props.form.validateFields((err, values) => {
      if (!err) {
        this.props.onSubmit()
            // edit
        axios.post('/api/v1/label', values)
          .then(resp => {
            message.success('成功添加')
          })
          .catch(err => {
            message.error(`添加失败，错误：${err}`)
          })
      }
    })
  }

  render() {
    const {
      getFieldDecorator, getFieldsError, getFieldError, isFieldTouched,
    } = this.props.form

    // Only show error after a field is touched.
    const nameError = isFieldTouched('name') && getFieldError('name')
    return (
      <Form onSubmit={this.handleSubmit}>
        <Form.Item
          {...FormItemLayout}
          validateStatus={nameError ? 'error' : ''}
          help={nameError || ''}
          label='分类'
        >
            {getFieldDecorator('name', {
            rules: [{ required: true, message: '请输入分类名!' }],
          })(
              <Input placeholder="请输入分类名" />
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

export default Form.create()(LabelForm)


