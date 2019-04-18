const FormItemLayout = {
  labelCol: {
    xs: { span: 24 },
    sm: { span: 4 },
  },
  wrapperCol: {
    xs: { span: 24 },
    sm: { span: 20 },
  },
}

const FormItemLayoutWithOutLabel = {
  wrapperCol: {
    xs: { span: 24, offset: 0 },
    sm: { span: 20, offset: 4 },
  },
}

const TwoColumnsFormItemLayout = {
  labelCol: {
    xs: { span: 20 },
    sm: { span: 8 },
  },
  wrapperCol: {
    xs: { span: 20 },
    sm: { span: 16 },
  },
}
const tailFormItemLayout = {
      wrapperCol: {
        xs: {
          span: 24,
          offset: 0,
        },
        sm: {
          span: 16,
          offset: 8,
        },
      },
    };

const ProductSessionKey = 'tao.product.id'
const PageNumSessionKey= 'tao.page.num'

export {
  FormItemLayout,
  FormItemLayoutWithOutLabel,
  TwoColumnsFormItemLayout,
  ProductSessionKey,
  PageNumSessionKey,
  tailFormItemLayout
}
