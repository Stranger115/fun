import React from 'react'
import ReactDOM from 'react-dom'
import { Provider } from 'mobx-react'
import { configure } from 'mobx'
import 'antd/dist/antd.css'
import moment from 'moment'
import 'moment/locale/zh-cn'

import App from './App'
import injects from './inject'
import './index.css'


configure({ enforceActions: true })

ReactDOM.render(<Provider {...injects}><App /></Provider>, document.getElementById('root'))
