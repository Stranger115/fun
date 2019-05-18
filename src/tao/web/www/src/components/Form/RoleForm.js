'use strict'

import React from 'react'
import {Form, Input, Button, message} from 'antd'
import { FormItemLayout, FormItemLayoutWithOutLabel } from "../../constants"
import axios from "axios";


const { TextArea } = Input;

function hasErrors(fieldsError) {
  return Object.keys(fieldsError).some(field => fieldsError[field])
}


export class RoleForm extends React.Component {
  constructor(props) {
    super(props)
    this.roles = null
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
        axios.post('/api/v1/add_role', values)
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
    const roleError = isFieldTouched('role') && getFieldError('role')
    const descriptionError = isFieldTouched('description') && getFieldError('description')
    return (
      <Form onSubmit={this.handleSubmit}>
        <Form.Item
          {...FormItemLayout}
          validateStatus={roleError ? 'error' : ''}
          help={roleError || ''}
          label='角色'
        >
            {getFieldDecorator('role', {
            rules: [{ required: true, message: '请输入角色名!' }],
          })(
              <Input placeholder="请输入角色名" />
          )}
        </Form.Item>
        <Form.Item
          {...FormItemLayout}
          validateStatus={descriptionError ? 'error' : ''}
          help={descriptionError || ''}
          label='说明'
        >
            {getFieldDecorator('description', {
            rules: [{ required: true, message: '请输入说明!' }],
          })(
              <TextArea rows={4}  placeholder="请输入说明"/>
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

export default Form.create()(RoleForm)


