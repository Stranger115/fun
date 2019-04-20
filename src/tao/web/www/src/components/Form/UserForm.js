'use strict'

import React from 'react'
import {Form, Select, Modal, Input, Row, Col, Icon, Button, message} from 'antd'
import axios from "axios";
import { FormItemLayout, FormItemLayoutWithOutLabel } from "../../constants"

const FormItem = Form.Item
const Option = Select.Option
export const EditableContext = React.createContext()

const EditableRow = ({ form, index, ...props }) => (
  <EditableContext.Provider value={form}>
    <tr {...props} />
  </EditableContext.Provider>
)


export const EditableFormRow = Form.create()(EditableRow)

export class EditableCell extends React.Component {
  constructor(props) {
    super(props)
    this.role = null
    }
  getInput = () => {
    if (this.props.dataIndex === 'role'){
      axios.get('/api/v1/get_role')
      .then(resp => {
         let role_des = resp.data.role
         this.role = this.role.filter(item => item.level === 0)
        })
      return <Select initialValue="1">
               <Option value="1">女</Option>
               <Option value="2">男</Option>
             </Select>
    }
    else if (this.props.dataIndex === 'sex'){
      return <Select initialValue="1">
               <Option value="1">女</Option>
               <Option value="2">男</Option>
             </Select>
    }

    return <Input style={{ width: '70%' }} />
  }
  render() {
    const {
      editing,
      dataIndex,
      title,
      inputType,
      record,
      index,
      ...restProps
    } = this.props
    return (
      <EditableContext.Consumer>
        {(form) => {
          const { getFieldDecorator } = form
          return (
            <td {...restProps}>
              {editing ? (
                <FormItem style={{ margin: 0 }}>
                  {getFieldDecorator(dataIndex, {
                    rules: [{
                      required: true,
                      message: `请输入 ${title}!`,
                    }],
                    initialValue: record[dataIndex],
                  })(this.getInput())}
                </FormItem>
              ) : restProps.children}
            </td>
          )
        }}
      </EditableContext.Consumer>
    )
  }
}


function hasErrors(fieldsError) {
  return Object.keys(fieldsError).some(field => fieldsError[field])
}


export class DNSForm extends React.Component {
  componentDidMount() {
    // To disabled submit button at the beginning.
    this.props.form.validateFields()
  }

  handleSubmit = (e) => {
    e.preventDefault()
    this.props.form.validateFields((err, values) => {
      if (!err) {
        this.props.onSubmit(values)
      }
    })
  }
  render() {
    const {
      getFieldDecorator, getFieldsError, getFieldError, isFieldTouched,
    } = this.props.form

    // Only show error after a field is touched.
    const fqdnError = isFieldTouched('fqdn') && getFieldError('fqdn')
    const ipError = isFieldTouched('ip') && getFieldError('ip')
    const nettypeError = isFieldTouched('nettype') && getFieldError('nettype')
    return (
      <Form onSubmit={this.handleSubmit}>
        <Form.Item
          {...FormItemLayout}
          validateStatus={fqdnError ? 'error' : ''}
          help={fqdnError || ''}
          label='域名'
        >
            {getFieldDecorator('fqdn', {
            rules: [{ required: true, message: '请输入DNS!' }],
          })(
              <Input placeholder="请输入DNS" />
          )}
        </Form.Item>
        <Form.Item
          {...FormItemLayout}
          validateStatus={ipError ? 'error' : ''}
          help={ipError || ''}
          label='IP地址'
        >
          {getFieldDecorator('ip', {
           rules: [{ required: true, message: '请输入IP!' }],
          })(
            <Input placeholder="请输入IP" />
         )}
         </Form.Item>
        <Form.Item
          {...FormItemLayout}
          validateStatus={nettypeError ? 'error' : ''}
          help={nettypeError || ''}
          label='网络类型'
        >
          {getFieldDecorator('nettype', {
            initialValue:'intranet',
            rules: [{ required: true, whitespace: true,  message: '请输入IP!' }],
          })(
            <Select placeholder="请选择配置类型">
              <Option value="intranet">内网IP</Option>
              <Option value="internet">外网IP</Option>
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

export default Form.create()(DNSForm)


