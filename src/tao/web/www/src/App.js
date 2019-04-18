'use strict'

import React, { Component } from 'react'
import { inject, observer } from 'mobx-react'
import { HashRouter, Route, Switch, Redirect } from 'react-router-dom'
import axios from 'axios'
import { Service } from 'axios-middleware'

import Main from './containers/Main'


const service = new Service(axios)

service.register({
    onResponseError(err) {
        if (err.response && err.response.status === 401) {
          window.location = '/'
          return
        }
        throw err
    }
})


@inject('sysStore', 'userActions', 'userStore')
@observer
class App extends Component {
  constructor(props) {
    super(props)
    this.state = {}
  }

  renderRouter() {
    return (
      <HashRouter>
        <Switch>
          <Route path='/' render={() => <Main />}/>
        </Switch>
      </HashRouter>
    )
  }

  render() {
    return this.renderRouter()
  }
}

export default App
